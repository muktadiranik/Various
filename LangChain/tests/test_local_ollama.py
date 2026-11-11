"""Verify local Ollama configuration without live providers or credentials."""

import asyncio
import importlib.util
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def chatbot():
    """Import 12.py without reading secrets or connecting to services."""
    path = Path(__file__).resolve().parents[1] / "12.py"
    spec = importlib.util.spec_from_file_location("local_ollama_chatbot", path)
    module = importlib.util.module_from_spec(spec)
    with (
        patch.dict("os.environ", {"DATABASE_URL": "sqlite://"}),
        patch("dotenv.load_dotenv", return_value=False),
    ):
        spec.loader.exec_module(module)
    yield module
    module.get_agent_executor.cache_clear()
    module.engine.dispose()


def test_no_cloud_ollama_client_or_tool_remains(chatbot):
    source = Path(chatbot.__file__).read_text(encoding="utf-8")
    assert "https://ollama.com" not in source
    assert "OLLAMA_API_KEY" not in source
    assert "ollama_web_search" not in source
    assert {tool.name for tool in chatbot.tools} == {
        "wolfram_alpha_search", "wikipedia_search", "arxiv_search",
        "pubmed_search", "duckduckgo_search", "tavily_search",
    }


def test_lifespan_does_not_construct_a_cloud_ollama_client(chatbot, monkeypatch):
    http_client = AsyncMock()
    http_client.__aenter__.return_value = http_client
    redis = AsyncMock()
    redis.__aenter__.return_value = redis
    monkeypatch.setattr(chatbot.httpx, "AsyncClient", MagicMock(return_value=http_client))
    monkeypatch.setattr(chatbot.Redis, "from_url", MagicMock(return_value=redis))
    monkeypatch.setattr(chatbot.Base.metadata, "create_all", MagicMock())
    monkeypatch.setattr(chatbot.engine, "dispose", MagicMock())
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)

    async def run():
        async with chatbot.lifespan(chatbot.app):
            assert chatbot.app.state.http_client is http_client
            assert chatbot.app.state.redis is redis
            assert not hasattr(chatbot.app.state, "ollama_search")

    with patch("ollama.AsyncClient", side_effect=AssertionError("Unexpected Ollama client at startup")):
        asyncio.run(run())
    http_client.__aexit__.assert_awaited_once()
    redis.__aexit__.assert_awaited_once()


@pytest.mark.parametrize(("question", "reply", "research"), [
    ("Hello!", "Hello! How can I help?", False),
    (
        "Write a Python sum function.",
        "```python\ndef sum_numbers(*numbers):\n    return sum(numbers)\n```",
        False,
    ),
    (
        "Explain a Python sum function with code.",
        "The star collects any number of arguments.\n\n"
        "```python\ndef sum_numbers(*numbers):\n    return sum(numbers)\n```",
        False,
    ),
    ("Search Wikipedia for Python.", "Python is a programming language.", True),
])
def test_model_requests_stay_local_without_a_cloud_key(
    chatbot, monkeypatch, question, reply, research
):
    """Use the real SDK and agent with controlled HTTP responses."""
    real_model_class = chatbot.ChatOllama
    models = []
    requests = []
    search = AsyncMock(return_value="Python is a programming language.")
    monkeypatch.setattr(chatbot.wikipedia_search, "coroutine", search)
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")

    def respond(request):
        assert request.url.host == "localhost"
        assert request.url.port == 11434
        assert request.url.path == "/api/chat"
        assert "authorization" not in request.headers
        body = json.loads(request.content)
        requests.append(body)
        assert body["model"] == "qwen2.5-coder:1.5b"
        assert body["options"]["temperature"] == 0
        assert {item["function"]["name"] for item in body["tools"]} == {
            tool.name for tool in chatbot.tools
        }
        message = {"role": "assistant", "content": reply}
        if research and len(requests) == 1:
            message = {
                "role": "assistant", "content": "",
                "tool_calls": [{"function": {
                    "name": "wikipedia_search", "arguments": {"query": "Python"},
                }}],
            }
        return httpx.Response(200, json={
            "model": "qwen2.5-coder:1.5b", "message": message,
            "done": True, "done_reason": "stop",
        })

    def create_model(**kwargs):
        assert kwargs == {
            "base_url": "http://localhost:11434", "model": "qwen2.5-coder:1.5b",
            "temperature": 0, "client_kwargs": {"timeout": 60.0},
        }
        kwargs["client_kwargs"]["transport"] = httpx.MockTransport(respond)
        model = real_model_class(**kwargs)
        models.append(model)
        return model

    monkeypatch.setattr(chatbot, "ChatOllama", create_model)
    chatbot.get_agent_executor.cache_clear()

    async def run():
        try:
            executor = chatbot.get_agent_executor()
            assert executor.max_execution_time == chatbot.AGENT_TIMEOUT
            assert executor.max_iterations == 15
            assert executor.handle_parsing_errors is True
            return await executor.ainvoke({"question": question, "chat_history": []})
        finally:
            for model in models:
                await model._async_client._client.aclose()
                model._client._client.close()

    try:
        assert asyncio.run(run())["output"] == reply
        assert len(requests) == (2 if research else 1)
        if research:
            search.assert_awaited_once_with(query="Python")
        else:
            search.assert_not_awaited()
    finally:
        chatbot.get_agent_executor.cache_clear()


@pytest.mark.parametrize("call_format", ["plain", "fenced", "query", "nested", "native", "native-nested"])
@pytest.mark.parametrize("outcome", ["success", "http-error", "missing-appid"])
def test_websocket_executes_qwen_tool_json_instead_of_displaying_it(
    chatbot, monkeypatch, call_format, outcome
):
    """Run the real SDK, agent, tool, and gateway with controlled HTTP replies."""
    real_model_class = chatbot.ChatOllama
    models = []
    model_requests = []
    wolfram_requests = []
    query = "integrate x^2 from 0 to 3"
    arguments = {"type": "string", "value": query}
    if call_format == "query":
        arguments = {"query": query}
    elif call_format in {"nested", "native-nested"}:
        arguments = {"query": arguments}
    payload = json.dumps({"name": "wolfram_alpha_search", "arguments": arguments})
    content = f"```json\n{payload}\n```" if call_format == "fenced" else payload
    message = {"role": "assistant", "content": content}
    if call_format in {"native", "native-nested"}:
        message = {
            "role": "assistant", "content": "",
            "tool_calls": [{"function": {"name": "wolfram_alpha_search", "arguments": arguments}}],
        }

    def respond(request):
        if request.url.host == "localhost":
            model_requests.append(request)
            assert len(model_requests) == 1, "A completed Wolfram result must not need another inference"
            return httpx.Response(200, json={
                "model": "qwen2.5-coder:1.5b", "message": message,
                "done": True, "done_reason": "stop",
            })
        assert request.url.host == "api.wolframalpha.com"
        wolfram_requests.append(request)
        assert request.url.params["input"] == query
        assert request.headers["user-agent"] == "KnowledgeChatbot/1.0"
        return httpx.Response(403 if outcome == "http-error" else 200, text=(
            '<queryresult success="true" error="false"><pod title="Result">'
            '<subpod><plaintext>9</plaintext></subpod></pod></queryresult>'
        ))

    def create_model(**kwargs):
        kwargs["client_kwargs"] = {
            **kwargs["client_kwargs"], "transport": httpx.MockTransport(respond),
        }
        model = real_model_class(**kwargs)
        models.append(model)
        return model

    expected = {
        "success": "### Result\n9",
        "http-error": "Wolfram Alpha search failed. Do NOT retry this query.",
        "missing-appid": "Wolfram Alpha AppID is not configured.",
    }[outcome]
    store = AsyncMock()
    monkeypatch.setattr(chatbot, "ChatOllama", create_model)
    monkeypatch.setattr(chatbot, "manager", chatbot.ConnectionManager())
    monkeypatch.setattr(chatbot, "load_chat_history", AsyncMock(return_value=[]))
    monkeypatch.setattr(chatbot, "store_chat_turn", store)
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    if outcome == "missing-appid":
        monkeypatch.delenv("WOLFRAM_ALPHA_APPID", raising=False)
    else:
        monkeypatch.setenv("WOLFRAM_ALPHA_APPID", "test-app-id-not-real")
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    monkeypatch.setattr(chatbot.app.state, "http_client", http_client, raising=False)
    chatbot.get_agent_executor.cache_clear()
    socket_client = TestClient(chatbot.app)  # Do not run lifespan or contact databases.

    async def close_clients():
        await http_client.aclose()
        for model in models:
            await model._async_client._client.aclose()
            model._client._client.close()

    try:
        with socket_client.websocket_connect("/ws/chat?session_id=tool-json-test") as websocket:
            websocket.send_text("Calculate the definite integral of x^2 from 0 to 3.")
            assert websocket.receive_text() == f"AI: {expected}"
        assert len(model_requests) == 1
        assert len(wolfram_requests) == (0 if outcome == "missing-appid" else 1)
        store.assert_awaited_once()
        assert store.await_args.args[1][-1].content == expected
    finally:
        socket_client.close()
        asyncio.run(close_clients())
        chatbot.get_agent_executor.cache_clear()


def test_saved_wolfram_failure_is_not_reported_without_a_current_tool_call(chatbot, monkeypatch):
    """A stale failure must cause a real lookup, not be saved as another failure."""
    real_model_class = chatbot.ChatOllama
    models = []
    model_requests = []
    wolfram_requests = []
    failure = "Wolfram Alpha search failed. Do NOT retry this query."
    question = "Calculate the definite integral of x^2 from 0 to 3."
    history = [chatbot.HumanMessage(content=question), chatbot.AIMessage(content=failure)]
    store = AsyncMock()

    def respond(request):
        if request.url.host == "localhost":
            model_requests.append(json.loads(request.content))
            assert len(model_requests) <= 2, "No extra inference is needed after the real result"
            content = failure if len(model_requests) == 1 else json.dumps({
                "name": "wolfram_alpha_search",
                "arguments": {"type": "string", "value": "integrate x^2 from 0 to 3"},
            })
            return httpx.Response(200, json={
                "model": "qwen2.5-coder:1.5b",
                "message": {"role": "assistant", "content": content},
                "done": True, "done_reason": "stop",
            })
        assert request.url.host == "api.wolframalpha.com"
        wolfram_requests.append(request)
        return httpx.Response(200, text=(
            '<queryresult success="true" error="false"><pod title="Result">'
            '<subpod><plaintext>9</plaintext></subpod></pod></queryresult>'
        ))

    def create_model(**kwargs):
        kwargs["client_kwargs"] = {
            **kwargs["client_kwargs"], "transport": httpx.MockTransport(respond),
        }
        model = real_model_class(**kwargs)
        models.append(model)
        return model

    monkeypatch.setattr(chatbot, "ChatOllama", create_model)
    monkeypatch.setattr(chatbot, "manager", chatbot.ConnectionManager())
    monkeypatch.setattr(chatbot, "load_chat_history", AsyncMock(return_value=history))
    monkeypatch.setattr(chatbot, "store_chat_turn", store)
    monkeypatch.setenv("WOLFRAM_ALPHA_APPID", "test-app-id-not-real")
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    monkeypatch.setattr(chatbot.app.state, "http_client", http_client, raising=False)
    chatbot.get_agent_executor.cache_clear()
    socket_client = TestClient(chatbot.app)

    async def close_clients():
        await http_client.aclose()
        for model in models:
            await model._async_client._client.aclose()
            model._client._client.close()

    try:
        with socket_client.websocket_connect("/ws/chat?session_id=stale-error-test") as websocket:
            websocket.send_text(question)
            assert websocket.receive_text() == "AI: ### Result\n9"
        assert len(model_requests) == 2
        assert any(
            "No Wolfram lookup has run in the current turn" in message.get("content", "")
            for message in model_requests[1]["messages"]
        )
        assert len(wolfram_requests) == 1
        store.assert_awaited_once()
        saved = store.await_args.args[1]
        assert [message.content for message in saved] == [question, failure, question, "### Result\n9"]
    finally:
        socket_client.close()
        asyncio.run(close_clients())
        chatbot.get_agent_executor.cache_clear()


def test_research_prompt_allows_a_new_turn_to_retry_a_previous_query(chatbot):
    system_prompt = chatbot.prompt.messages[0].prompt.template
    assert "per conversation" not in system_prompt
    assert "current turn" in system_prompt


def test_real_wolfram_failure_remains_authoritative(chatbot):
    failure = "Wolfram Alpha search failed. Do NOT retry this query."
    finish = chatbot.AgentFinish(return_values={"output": failure}, log=failure)
    action = chatbot.AgentAction(
        tool="wolfram_alpha_search", tool_input={"query": "integrate x^2 from 0 to 3"}, log="",
    )
    assert chatbot._resolve_research_result({
        "agent_result": finish, "intermediate_steps": [(action, failure)],
    }) is finish
