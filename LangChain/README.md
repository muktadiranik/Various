# Knowledge chatbot (`10.py`)

## Chat storage

- Each completed exchange is committed to PostgreSQL before its successful
  WebSocket reply is sent: one `human` row and one `ai` row. There is no
  application-imposed limit on the number of stored messages.
- Both rows are saved in one transaction. Existing transcript rows are never
  deleted, and re-saving the same transcript does not duplicate messages.
- Redis is a best-effort cache with a 24-hour TTL, not durable storage. Cache
  failure, expiration, or an outdated snapshot does not hide saved messages.
  History is read from PostgreSQL; compatible newer Redis entries left by the
  previous batched writer are included in the next successful save.
- Database failures return an error instead of a successful chat reply. The
  application no longer depends on a five-turn batch or a clean disconnect to
  persist completed exchanges. A question whose agent call fails before an
  answer is produced is not a completed exchange and is not stored.

The old five-exchange flush interval made PostgreSQL update in batches of **10
rows**, not a maximum of 10 rows. Messages that existed only in Redis and have
already expired or been deleted cannot be recovered by this change.

## Reading saved chats

Read endpoints remain paginated; their `limit` parameters do not restrict storage:

- `/conversations?limit=20&offset=0`: session summaries.
- `/conversations/{session_id}?limit=50&offset=0`: messages for one session.
- `/conversations/all/grouped?limit=10&offset=0`: full messages for 10 sessions.

Use `meta.total_items` and `meta.has_next`, increasing `offset` by `limit` to
retrieve subsequent pages.

## Regression tests

From the repository root using the existing virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest LangChain/tests/test_chat_persistence.py -q -p no:cacheprovider
```

Tests exercise the real WebSocket handler, SQLAlchemy persistence, and REST
pagination against an isolated SQLite database with in-memory Redis and agent
test doubles. They do not contact PostgreSQL, Redis, or external model providers.

## Code-writing requests (`12.py`)

Explicit requests such as "Write a function that accepts an arbitrary number of
inputs and returns their sum" use a tool-free coding prompt. No tool schemas are
sent to Qwen on this path: the requested function is source code to generate, not
a tool to invoke. This avoids the small model returning an invented `sum` tool
call instead of Python code. Conversation history is preserved.
Restart the app after updating. If a chat already contains incorrect tool-call
replies, start a new conversation: the small model may still imitate those old
answers, even with the corrected prompt.

Requests to search external sources still use the tool agent.

## Text-only operation (`12.py`)

The application accepts text messages and returns text or Markdown. Its six
research tools accept text queries and return text results. No device capture
or image, video, or audio processing is available.

Text-routing regression tests use a deterministic model and search test double,
without accessing Ollama or external providers:

```powershell
.\.venv\Scripts\python.exe -m pytest LangChain/tests/test_chatbot_routing.py -q -p no:cacheprovider
```
