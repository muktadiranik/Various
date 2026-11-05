"""Regression tests for durable chat storage without external services."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from redis.exceptions import RedisError
from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


class MemoryRedis:
    """Small Redis test double preserving list ordering and transactions."""

    def __init__(self):
        self.values = {}
        self.fail_reads = False
        self.fail_writes = False

    async def lrange(self, key, start, end):
        if self.fail_reads:
            raise RedisError("Cache unavailable")
        values = self.values.get(key, [])
        return values[start:] if end == -1 else values[start : end + 1]

    def pipeline(self, transaction=True):
        return MemoryPipeline(self)


class MemoryPipeline:
    def __init__(self, redis):
        self.redis = redis
        self.commands = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def delete(self, key):
        self.commands.append(("delete", key, ()))
        return self

    def lpush(self, key, *values):
        self.commands.append(("lpush", key, values))
        return self

    def expire(self, key, ttl):
        self.commands.append(("expire", key, (ttl,)))
        return self

    def incr(self, key):
        self.commands.append(("incr", key, ()))
        return self

    async def execute(self):
        if self.redis.fail_writes:
            raise RedisError("Cache unavailable")
        results = []
        for command, key, values in self.commands:
            if command == "delete":
                results.append(int(self.redis.values.pop(key, None) is not None))
            elif command == "lpush":
                target = self.redis.values.setdefault(key, [])
                target[0:0] = reversed(values)
                results.append(len(target))
            elif command == "incr":
                self.redis.values[key] = self.redis.values.get(key, 0) + 1
                results.append(self.redis.values[key])
            else:
                results.append(True)
        return results


@pytest.fixture(scope="module")
def chatbot():
    """Import the real app without reading credentials or connecting to Postgres."""
    path = Path(__file__).resolve().parents[1] / "10.py"
    spec = importlib.util.spec_from_file_location("knowledge_chatbot", path)
    module = importlib.util.module_from_spec(spec)
    with (
        patch.dict("os.environ", {"DATABASE_URL": "sqlite://"}),
        patch("dotenv.load_dotenv", return_value=False),
    ):
        spec.loader.exec_module(module)
    yield module
    module.engine.dispose()


@pytest.fixture
def app_state(chatbot, tmp_path, monkeypatch):
    """Use a real isolated SQL database and deterministic cache/agent doubles."""
    engine = create_engine(f"sqlite:///{(tmp_path / 'chats.db').as_posix()}")
    chatbot.Base.metadata.create_all(engine)
    monkeypatch.setattr(chatbot, "SessionLocal", sessionmaker(bind=engine))
    monkeypatch.setattr(chatbot, "manager", chatbot.ConnectionManager())
    redis = MemoryRedis()
    monkeypatch.setattr(chatbot.app.state, "redis", redis, raising=False)
    agent = SimpleNamespace(ainvoke=AsyncMock(side_effect=lambda inputs: {"output": f"Answer: {inputs['question']}"}))
    monkeypatch.setattr(chatbot, "get_agent_executor", lambda: agent)
    # Do not run lifespan: these tests must not contact Redis or any HTTP provider.
    client = TestClient(chatbot.app)
    yield SimpleNamespace(app=chatbot, redis=redis, agent=agent, client=client)
    client.close()
    engine.dispose()


def transcript(app, session_id):
    return [(message.type, message.content) for message in app.load_persisted_messages(session_id)]


def make_messages(app, count):
    return [
        message
        for index in range(count)
        for message in (
            app.HumanMessage(content=f"Question {index}"),
            app.AIMessage(content=f"Answer {index}"),
        )
    ]


def seed_cache(state, session_id, messages):
    state.redis.values[f"message_store:{session_id}"] = [
        state.app.json.dumps(state.app.message_to_dict(message)) for message in reversed(messages)
    ]


def test_every_turn_is_committed_before_reply_beyond_ten_rows(app_state):
    state = app_state
    expected = []
    with state.client.websocket_connect("/ws/chat?session_id=long-chat") as websocket:
        for index in range(12):
            question = f"Question {index}"
            websocket.send_text(question)
            assert websocket.receive_text() == f"AI: Answer: {question}"
            expected.extend([("human", question), ("ai", f"Answer: {question}")])
            # Assert while the connection is open, not after a disconnect flush.
            assert transcript(state.app, "long-chat") == expected
    assert transcript(state.app, "long-chat") == expected


def test_reconnect_recovers_history_after_cache_loss(app_state):
    state = app_state
    with state.client.websocket_connect("/ws/chat?session_id=reconnect") as websocket:
        websocket.send_text("First")
        assert websocket.receive_text() == "AI: Answer: First"
    state.redis.values.clear()
    with state.client.websocket_connect("/ws/chat?session_id=reconnect") as websocket:
        websocket.send_text("Second")
        assert websocket.receive_text() == "AI: Answer: Second"
        assert len(transcript(state.app, "reconnect")) == 4
    inputs = state.agent.ainvoke.call_args.args[0]
    assert [(message.type, message.content) for message in inputs["chat_history"]] == [
        ("human", "First"),
        ("ai", "Answer: First"),
    ]


def test_redis_outage_does_not_prevent_durable_chats(app_state):
    state = app_state
    state.redis.fail_reads = state.redis.fail_writes = True
    with state.client.websocket_connect("/ws/chat?session_id=no-cache") as websocket:
        for index in range(2):
            websocket.send_text(f"Question {index}")
            assert websocket.receive_text() == f"AI: Answer: Question {index}"
            assert len(transcript(state.app, "no-cache")) == 2 * (index + 1)
    assert len(state.agent.ainvoke.call_args.args[0]["chat_history"]) == 2


def test_failed_cache_refresh_cannot_hide_committed_messages(app_state):
    state = app_state
    messages = make_messages(state.app, 1)
    state.app.persist_messages_to_postgres("stale-cache", messages)
    seed_cache(state, "stale-cache", messages)
    state.redis.fail_writes = True
    with state.client.websocket_connect("/ws/chat?session_id=stale-cache") as websocket:
        for index in range(3):
            websocket.send_text(f"New {index}")
            assert websocket.receive_text() == f"AI: Answer: New {index}"
            assert len(transcript(state.app, "stale-cache")) == 4 + 2 * index
    assert len(state.agent.ainvoke.call_args.args[0]["chat_history"]) == 6


def test_existing_unflushed_redis_messages_are_preserved(app_state):
    state = app_state
    messages = make_messages(state.app, 7)
    state.app.persist_messages_to_postgres("legacy", messages[:10])
    seed_cache(state, "legacy", messages)
    with state.client.websocket_connect("/ws/chat?session_id=legacy") as websocket:
        websocket.send_text("Next")
        assert websocket.receive_text() == "AI: Answer: Next"
        assert len(transcript(state.app, "legacy")) == 16
        assert transcript(state.app, "legacy")[:14] == [(message.type, message.content) for message in messages]


@pytest.mark.parametrize("cache_turns", [1, 3])
def test_conflicting_cache_cannot_replace_database_history(app_state, cache_turns):
    state = app_state
    messages = make_messages(state.app, 2)
    state.app.persist_messages_to_postgres("conflict", messages)
    cached = make_messages(state.app, cache_turns)
    cached[0] = state.app.HumanMessage(content="Wrong history")
    seed_cache(state, "conflict", cached)
    with state.client.websocket_connect("/ws/chat?session_id=conflict") as websocket:
        websocket.send_text("Next")
        assert websocket.receive_text() == "AI: Answer: Next"
        assert len(transcript(state.app, "conflict")) == 6
        assert transcript(state.app, "conflict")[:4] == [(message.type, message.content) for message in messages]


@pytest.mark.parametrize("cache_entries", [["not-json"], ['{"type":"unknown","data":{}}']])
def test_invalid_cache_does_not_block_saved_history(app_state, cache_entries):
    state = app_state
    state.app.persist_messages_to_postgres("invalid-cache", make_messages(state.app, 1))
    state.redis.values["message_store:invalid-cache"] = cache_entries
    with state.client.websocket_connect("/ws/chat?session_id=invalid-cache") as websocket:
        websocket.send_text("Next")
        assert websocket.receive_text() == "AI: Answer: Next"
        assert len(transcript(state.app, "invalid-cache")) == 4


def test_database_failure_rolls_back_turn_without_acknowledging_success(app_state):
    state = app_state

    def fail_after_insert(mapper, connection, target):
        if target.role == "ai":
            raise SQLAlchemyError("Transaction failed after inserts")

    event.listen(state.app.ChatLog, "after_insert", fail_after_insert)
    try:
        with state.client.websocket_connect("/ws/chat?session_id=db-failure") as websocket:
            websocket.send_text("Unsaved")
            response = websocket.receive_text()
            assert "could not be saved" in response
            # Both inserts were issued, but the failed transaction leaves no rows.
            assert transcript(state.app, "db-failure") == []
            assert state.redis.values == {}
    finally:
        event.remove(state.app.ChatLog, "after_insert", fail_after_insert)
    with state.client.websocket_connect("/ws/chat?session_id=db-failure") as websocket:
        websocket.send_text("Retry")
        assert websocket.receive_text() == "AI: Answer: Retry"
        assert transcript(state.app, "db-failure") == [("human", "Retry"), ("ai", "Answer: Retry")]


def test_repeated_snapshots_append_without_duplicates_or_deletions(app_state):
    app = app_state.app
    messages = make_messages(app, 15)
    app.persist_messages_to_postgres("append-only", messages[:10])
    app.persist_messages_to_postgres("append-only", messages[:10])
    app.persist_messages_to_postgres("append-only", messages)
    assert len(transcript(app, "append-only")) == 30
    with pytest.raises(ValueError):
        app.persist_messages_to_postgres("append-only", messages[:2])
    assert len(transcript(app, "append-only")) == 30


def test_grouped_pagination_does_not_limit_database_storage(app_state):
    state = app_state
    for index in range(12):
        state.app.persist_messages_to_postgres(f"session-{index:02}", make_messages(state.app, 1))
    response = state.client.get("/conversations/all/grouped")
    assert response.status_code == 200
    first = response.json()
    assert first["meta"]["total_items"] == 12
    assert first["meta"]["has_next"] is True
    assert len(first["data"]) == 10
    response = state.client.get("/conversations/all/grouped?offset=10")
    assert response.status_code == 200
    second = response.json()
    assert len(second["data"]) == 2
    assert second["meta"]["has_next"] is False
    assert set(first["data"]).isdisjoint(second["data"])


def test_transcript_pagination_keeps_messages_beyond_first_page(app_state):
    state = app_state
    state.app.persist_messages_to_postgres("paged", make_messages(state.app, 15))
    ids = []
    for offset in (0, 10, 20):
        response = state.client.get(f"/conversations/paged?limit=10&offset={offset}")
        assert response.status_code == 200
        page = response.json()
        assert page["meta"]["total_items"] == 30
        assert len(page["messages"]) == 10
        ids.extend(message["id"] for message in page["messages"])
    assert len(set(ids)) == 30
