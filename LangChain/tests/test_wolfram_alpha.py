"""Test only the Wolfram tool without starting the app or other providers."""

import ast
import asyncio
import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from langchain_core.tools import tool


SUCCESS_XML = (
    '<queryresult success="true" error="false">'
    '<pod title="Result"><subpod><plaintext>9</plaintext></subpod></pod>'
    '</queryresult>'
)


@pytest.fixture
def wolfram_tool(monkeypatch):
    """Compile the original tool and constants only, without importing the app."""
    path = Path(__file__).resolve().parents[1] / "12.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    constants = {"RESULT_SEPARATOR", "PREFERRED_WOLFRAM_PODS"}
    nodes = [
        node for node in tree.body
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id in constants for target in node.targets)
        ) or (isinstance(node, ast.AsyncFunctionDef) and node.name == "wolfram_alpha_search")
    ]
    namespace = {
        "__name__": "isolated_wolfram_tests",
        "httpx": httpx, "ET": ET, "os": os, "tool": tool,
        "logger": logging.getLogger("isolated_wolfram_tests"),
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    monkeypatch.setenv("WOLFRAM_ALPHA_APPID", "test-app-id-not-real")
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")

    def invoke(handler, query="integrate x^2 from 0 to 3"):
        async def run():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                namespace["app"] = SimpleNamespace(state=SimpleNamespace(http_client=client))
                return await namespace["wolfram_alpha_search"].ainvoke({"query": query})

        return asyncio.run(run())

    return invoke


def test_application_user_agent_avoids_upstream_default_client_rejection(wolfram_tool):
    """Reproduce the live 403/200 distinction observed for the User-Agent."""
    requests = []

    def respond(request):
        requests.append(request)
        if request.headers["user-agent"] != "KnowledgeChatbot/1.0":
            return httpx.Response(403, text="<html>403 Forbidden nginx</html>")
        return httpx.Response(200, text=SUCCESS_XML)

    assert wolfram_tool(respond) == "### Result\n9"
    assert len(requests) == 1


def test_https_endpoint_credentials_and_query_encoding_are_preserved(wolfram_tool):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, text=SUCCESS_XML)

    assert wolfram_tool(respond, query="integrate x^2 + 0 from 0 to 3") == "### Result\n9"
    assert len(requests) == 1
    request = requests[0]
    assert request.url.scheme == "https"
    assert request.url.host == "api.wolframalpha.com"
    assert request.url.path == "/v2/query"
    assert dict(request.url.params) == {
        "appid": "test-app-id-not-real",
        "input": "integrate x^2 + 0 from 0 to 3",
        "format": "plaintext",
    }


def test_missing_appid_does_not_make_a_request(wolfram_tool, monkeypatch):
    monkeypatch.delenv("WOLFRAM_ALPHA_APPID", raising=False)

    def unexpected_request(request):
        pytest.fail("Missing credentials must not cause an HTTP request")

    assert wolfram_tool(unexpected_request) == "Wolfram Alpha AppID is not configured."


@pytest.mark.parametrize("status_code", [401, 403, 429, 503])
def test_http_failures_are_not_retried_or_promoted_to_success(wolfram_tool, status_code):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(status_code, text=SUCCESS_XML)

    assert wolfram_tool(respond) == "Wolfram Alpha search failed. Do NOT retry this query."
    assert len(requests) == 1


def test_malformed_xml_remains_a_failure(wolfram_tool):
    assert wolfram_tool(lambda request: httpx.Response(200, text="<queryresult")) == (
        "Wolfram Alpha search failed. Do NOT retry this query."
    )


def test_transport_timeout_is_not_retried(wolfram_tool):
    requests = []

    def timeout(request):
        requests.append(request)
        raise httpx.ReadTimeout("provider did not respond", request=request)

    assert wolfram_tool(timeout) == "Wolfram Alpha search failed. Do NOT retry this query."
    assert len(requests) == 1


def test_preferred_pod_formatting_is_unchanged(wolfram_tool):
    xml = (
        '<queryresult success="true" error="false">'
        '<pod title="Input"><subpod><plaintext>integrate x^2</plaintext></subpod></pod>'
        '<pod title="Result"><subpod><plaintext>9</plaintext></subpod></pod></queryresult>'
    )
    assert wolfram_tool(lambda request: httpx.Response(200, text=xml)) == (
        "### Input\nintegrate x^2\n\n---\n\n### Result\n9"
    )
