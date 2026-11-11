"""Test text-only chatbot routing without contacting external services."""

import asyncio
import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult


@pytest.fixture(scope="module")
def chatbot():
    """Import the app without reading credentials or connecting to a database."""
    path = Path(__file__).resolve().parents[1] / "12.py"
    spec = importlib.util.spec_from_file_location("text_chatbot", path)
    module = importlib.util.module_from_spec(spec)
    with (
        patch.dict("os.environ", {
            "DATABASE_URL": "sqlite://",
            "LANGSMITH_TRACING": "false",
            "LANGCHAIN_TRACING_V2": "false",
        }),
        patch("dotenv.load_dotenv", return_value=False),
    ):
        spec.loader.exec_module(module)
    yield module
    module.engine.dispose()


class TextChatModel(FakeMessagesListChatModel):
    """Model test double that accepts tool binding without any HTTP calls."""

    def bind_tools(self, tools, **kwargs):
        return self.bind(tools=tools, **kwargs)


def test_registered_tools_are_text_search_only(chatbot):
    assert {tool.name for tool in chatbot.tools} == {
        "wolfram_alpha_search",
        "wikipedia_search",
        "arxiv_search",
        "pubmed_search",
        "duckduckgo_search",
        "tavily_search",
    }
    for tool in chatbot.tools:
        properties = tool.args_schema.model_json_schema()["properties"]
        assert set(properties) == {"query"}
        assert properties["query"]["type"] == "string"


@pytest.mark.parametrize("question", [
    "Write a function that accepts an arbitrary number of inputs and returns their sum.",
    "Please write a Python function that formats text.",
    "Can you please create a JavaScript function to add numbers?",
    "Implement a class for chat history.",
    "Generate code that searches Wikipedia.",
    "Refactor this function to avoid duplication.",
])
def test_code_writing_requests_use_direct_path(chatbot, question):
    assert chatbot._is_code_writing_request({"question": question})


@pytest.mark.parametrize("question", [
    "Search Wikipedia for the history of Python.",
    "What is the latest Python release?",
    "Write a summary of the latest news.",
    "Hello!",
])
def test_tool_and_general_requests_keep_agent_path(chatbot, question):
    assert not chatbot._is_code_writing_request({"question": question})


def test_sum_function_request_returns_code_without_tool_schemas(chatbot, monkeypatch):
    code = "```python\ndef sum_numbers(*numbers):\n    return sum(numbers)\n```"
    model = TextChatModel(responses=[AIMessage(content=code)])
    generate = AsyncMock(return_value=ChatResult(generations=[
        ChatGeneration(message=AIMessage(content=code))
    ]))
    monkeypatch.setattr(TextChatModel, "_agenerate", generate)
    monkeypatch.setattr(chatbot, "ChatOllama", MagicMock(return_value=model))
    chatbot.get_agent_executor.cache_clear()
    try:
        result = asyncio.run(chatbot.get_agent_executor().ainvoke({
            "question": "Write a function that accepts an arbitrary number of inputs and returns their sum.",
            "chat_history": [],
        }))
        assert result["output"] == code
        generate.assert_awaited_once()
        assert "tools" not in generate.await_args.kwargs
    finally:
        chatbot.get_agent_executor.cache_clear()


def test_native_text_search_tool_still_runs(chatbot, monkeypatch):
    search = AsyncMock(return_value="Python is a programming language.")
    monkeypatch.setattr(chatbot.wikipedia_search, "coroutine", search)
    model = TextChatModel(responses=[
        AIMessage(content="", tool_calls=[{
            "name": "wikipedia_search", "args": {"query": "Python"}, "id": "search-1"
        }]),
        AIMessage(content="Python is a programming language."),
    ])
    monkeypatch.setattr(chatbot, "ChatOllama", MagicMock(return_value=model))
    chatbot.get_agent_executor.cache_clear()
    try:
        result = asyncio.run(chatbot.get_agent_executor().ainvoke({
            "question": "Search Wikipedia for Python.", "chat_history": []
        }))
        assert result["output"] == "Python is a programming language."
        search.assert_awaited_once_with(query="Python")
    finally:
        chatbot.get_agent_executor.cache_clear()


def test_general_text_reply_is_preserved(chatbot, monkeypatch):
    model = TextChatModel(responses=[AIMessage(content="Hello! How can I help?")])
    monkeypatch.setattr(chatbot, "ChatOllama", MagicMock(return_value=model))
    chatbot.get_agent_executor.cache_clear()
    try:
        result = asyncio.run(chatbot.get_agent_executor().ainvoke({
            "question": "Hello!", "chat_history": []
        }))
        assert result["output"] == "Hello! How can I help?"
    finally:
        chatbot.get_agent_executor.cache_clear()
