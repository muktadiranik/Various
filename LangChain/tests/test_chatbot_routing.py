"""Test the shared local-model agent and research-call adapter in isolation."""

import asyncio
import importlib.util
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult


@pytest.fixture(scope="module")
def chatbot():
    """Import the app without reading credentials or connecting to services."""
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
    module.get_agent_executor.cache_clear()
    module.engine.dispose()


class TextChatModel(FakeMessagesListChatModel):
    """Accept tool binding while keeping model responses deterministic."""

    def bind_tools(self, tools, **kwargs):
        return self.bind(tools=tools, **kwargs)


def test_registered_tools_are_text_search_only(chatbot):
    assert {registered.name for registered in chatbot.tools} == {
        "wolfram_alpha_search", "wikipedia_search", "arxiv_search",
        "pubmed_search", "duckduckgo_search", "tavily_search",
    }
    for registered in chatbot.tools:
        properties = registered.args_schema.model_json_schema()["properties"]
        assert set(properties) == {"query"}
        assert properties["query"]["type"] == "string"


@pytest.mark.parametrize(("question", "reply"), [
    ("Hello!", "Hello! How can I help?"),
    ("What is recursion?", "Recursion is when a function calls itself."),
    (
        "Write a Python sum function.",
        "```python\ndef sum_numbers(*numbers):\n    return sum(numbers)\n```",
    ),
    (
        "Write a Python sum function and explain it.",
        "The star collects any number of arguments.\n\n"
        "```python\ndef sum_numbers(*numbers):\n    return sum(numbers)\n```",
    ),
    (
        "Explain a Python list comprehension with an example.",
        "A list comprehension builds a list from an iterable.\n\n"
        "```python\nsquares = [n * n for n in range(5)]\n```",
    ),
])
def test_shared_agent_preserves_text_code_and_mixed_replies(chatbot, monkeypatch, question, reply):
    model = TextChatModel(responses=[AIMessage(content=reply)])
    generate = AsyncMock(return_value=ChatResult(generations=[
        ChatGeneration(message=AIMessage(content=reply)),
    ]))
    monkeypatch.setattr(TextChatModel, "_agenerate", generate)
    monkeypatch.setattr(chatbot, "ChatOllama", MagicMock(return_value=model))
    chatbot.get_agent_executor.cache_clear()
    try:
        result = asyncio.run(chatbot.get_agent_executor().ainvoke({
            "question": question, "chat_history": [],
        }))
        assert result["output"] == reply
        generate.assert_awaited_once()
        assert {registered.name for registered in generate.await_args.kwargs["tools"]} == {
            registered.name for registered in chatbot.tools
        }
    finally:
        chatbot.get_agent_executor.cache_clear()


def test_native_text_search_tool_still_runs(chatbot, monkeypatch):
    search = AsyncMock(return_value="Python is a programming language.")
    monkeypatch.setattr(chatbot.wikipedia_search, "coroutine", search)
    model = TextChatModel(responses=[
        AIMessage(content="", tool_calls=[{
            "name": "wikipedia_search", "args": {"query": "Python"}, "id": "search-1",
        }]),
        AIMessage(content="Python is a programming language."),
    ])
    monkeypatch.setattr(chatbot, "ChatOllama", MagicMock(return_value=model))
    chatbot.get_agent_executor.cache_clear()
    try:
        result = asyncio.run(chatbot.get_agent_executor().ainvoke({
            "question": "Search Wikipedia for Python.", "chat_history": [],
        }))
        assert result["output"] == "Python is a programming language."
        search.assert_awaited_once_with(query="Python")
    finally:
        chatbot.get_agent_executor.cache_clear()


@pytest.mark.parametrize("arguments", [
    {"query": "integrate x^2 from 0 to 3"},
    {"type": "string", "value": "integrate x^2 from 0 to 3"},
    {"query": {"type": "string", "value": "integrate x^2 from 0 to 3"}},
    "  integrate x^2 from 0 to 3  ",
])
def test_query_arguments_are_normalized(chatbot, arguments):
    assert chatbot._normalize_query_arguments(arguments) == {"query": "integrate x^2 from 0 to 3"}


@pytest.mark.parametrize("arguments", [
    None, [], {"query": " "}, {"query": 9},
    {"type": "array", "value": []}, {"type": "string", "value": []},
    {"query": "integrate x^2", "unexpected": "value"},
])
def test_invalid_query_arguments_are_rejected(chatbot, arguments):
    with pytest.raises(chatbot.InvalidAssistantReply):
        chatbot._normalize_query_arguments(arguments)


@pytest.mark.parametrize("argument_key", ["arguments", "args"])
@pytest.mark.parametrize("name", [
    "wolfram_alpha_search", "wikipedia_search", "arxiv_search",
    "pubmed_search", "duckduckgo_search", "tavily_search",
])
def test_plain_json_for_registered_tools_becomes_an_executable_action(chatbot, name, argument_key):
    output = json.dumps({"name": name, argument_key: {"type": "string", "value": "example query"}})
    actions = chatbot._resolve_research_result({
        "agent_result": chatbot.AgentFinish(return_values={"output": output}, log=output),
    })
    assert len(actions) == 1
    assert actions[0].tool == name
    assert actions[0].tool_input == {"query": "example query"}
    assert actions[0].message_log[0].tool_calls[0]["args"] == {"query": "example query"}
    assert actions[0].message_log[0].tool_calls[0]["id"] == actions[0].tool_call_id


def test_native_tool_arguments_and_scratchpad_are_normalized(chatbot):
    arguments = {"type": "string", "value": "integrate x^2 from 0 to 3"}
    message = AIMessage(content="", tool_calls=[{
        "name": "wolfram_alpha_search", "args": arguments, "id": "native-1",
    }])
    original = chatbot.ToolAgentAction(
        tool="wolfram_alpha_search", tool_input=arguments, log="",
        tool_call_id="native-1", message_log=[message],
    )
    actions = chatbot._resolve_research_result({"agent_result": [original]})
    assert actions[0].tool_input == {"query": "integrate x^2 from 0 to 3"}
    assert actions[0].message_log[0].tool_calls[0]["args"] == actions[0].tool_input
    assert actions[0].tool_call_id == "native-1"


def test_unregistered_tool_json_cannot_execute_arbitrary_functions(chatbot):
    output = '{"name": "run_shell", "arguments": {"query": "anything"}}'
    with pytest.raises(chatbot.InvalidAssistantReply):
        chatbot._resolve_research_result({
            "agent_result": chatbot.AgentFinish(return_values={"output": output}, log=output),
        })


@pytest.mark.parametrize("output", ["The answer is 9.", '{"result": 9}'])
def test_ordinary_research_answers_are_preserved(chatbot, output):
    finish = chatbot.AgentFinish(return_values={"output": output}, log=output)
    assert chatbot._resolve_research_result({"agent_result": finish}) is finish


@pytest.mark.parametrize("observation", [
    "### Result\n9", "Wolfram Alpha AppID is not configured.",
    "Wolfram Alpha search failed. Do NOT retry this query.",
])
def test_repeated_tool_calls_return_the_actual_observation(chatbot, observation):
    output = json.dumps({
        "name": "wolfram_alpha_search",
        "arguments": {"type": "string", "value": "integrate x^2 from 0 to 3"},
    })
    finish = chatbot.AgentFinish(return_values={"output": output}, log=output)
    action = chatbot._resolve_research_result({"agent_result": finish})[0]
    repeated = chatbot._resolve_research_result({
        "agent_result": finish, "intermediate_steps": [(action, observation)],
    })
    assert isinstance(repeated, chatbot.AgentFinish)
    assert repeated.return_values["output"] == observation


def test_missing_wolfram_appid_returns_setup_error_without_http(chatbot, monkeypatch):
    payload = json.dumps({
        "name": "wolfram_alpha_search",
        "arguments": {"type": "string", "value": "integrate x^2 from 0 to 3"},
    })
    model = TextChatModel(responses=[AIMessage(content=payload)])
    client = MagicMock()
    monkeypatch.delenv("WOLFRAM_ALPHA_APPID", raising=False)
    monkeypatch.setattr(chatbot.app.state, "http_client", client, raising=False)
    monkeypatch.setattr(chatbot, "ChatOllama", MagicMock(return_value=model))
    chatbot.get_agent_executor.cache_clear()
    try:
        result = asyncio.run(chatbot.get_agent_executor().ainvoke({
            "question": "Use Wolfram Alpha to calculate an integral.", "chat_history": [],
        }))
        assert result["output"] == "Wolfram Alpha AppID is not configured."
        client.get.assert_not_called()
    finally:
        chatbot.get_agent_executor.cache_clear()


@pytest.mark.parametrize(("question", "reply"), [
    ("Explain recursion.", "Recursion is when a function calls itself."),
    (
        "Write a Python sum function and explain it.",
        "This accepts any number of inputs.\n\n"
        "```python\ndef sum_numbers(*numbers):\n    return sum(numbers)\n```",
    ),
])
def test_websocket_sends_and_stores_text_and_code_unchanged(chatbot, monkeypatch, question, reply):
    model = TextChatModel(responses=[AIMessage(content=reply)])
    store = AsyncMock()
    monkeypatch.setattr(chatbot, "ChatOllama", MagicMock(return_value=model))
    monkeypatch.setattr(chatbot, "load_chat_history", AsyncMock(return_value=[]))
    monkeypatch.setattr(chatbot, "store_chat_turn", store)
    monkeypatch.setattr(chatbot, "manager", chatbot.ConnectionManager())
    chatbot.get_agent_executor.cache_clear()
    client = TestClient(chatbot.app)  # Skip lifespan: no database or Redis connections.
    try:
        with client.websocket_connect("/ws/chat?session_id=mixed-reply") as websocket:
            websocket.send_text(question)
            assert websocket.receive_text() == f"AI: {reply}"
        store.assert_awaited_once()
        session_id, messages = store.await_args.args
        assert session_id == "mixed-reply"
        assert [message.content for message in messages] == [question, reply]
    finally:
        client.close()
        chatbot.get_agent_executor.cache_clear()
