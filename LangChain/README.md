# Knowledge chatbots (`10.py` and `12.py`)

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
.\.venv\Scripts\python.exe -B -m pytest LangChain/tests -q -p no:cacheprovider
```

Tests exercise the real WebSocket handler, SQLAlchemy persistence, and REST
pagination against an isolated SQLite database with in-memory Redis and agent
test doubles. They do not contact PostgreSQL, Redis, or external model providers.

## Local Ollama (`12.py`)

`12.py` follows the shared tool-calling-agent structure of `10.py`, but uses
`qwen2.5-coder:1.5b` at `http://localhost:11434`. It does not create an Ollama
cloud client or require `OLLAMA_API_KEY`. Ollama's cloud-only web-search tool is
not registered; DuckDuckGo and optional Tavily remain available for web searches.

Install the model, keep Ollama running, and start the app:

```powershell
ollama pull qwen2.5-coder:1.5b
python LangChain/12.py
```

Database, Redis, and optional search-provider settings are loaded from
`LangChain/.env`. External research providers still require network access and
their own credentials where applicable. Never commit `.env` or share request
URLs containing an AppID.

Text, code, and mixed replies use the same agent. Tool schemas are available on
all requests; there is no separate tool-free coding path. Ordinary final text
and Markdown code blocks are preserved by the WebSocket gateway.

## Research tool calls (`12.py`)

If Qwen emits a registered research tool call as plain or fenced JSON, the agent
converts it into an actual invocation instead of displaying the JSON. Both the
normal `query` argument and Qwen's `type: string` / `value` shape (including when
nested inside `query`) are normalized to a non-empty text query for native and
text-only calls. Only the six registered research tools can execute; arbitrary
function names are rejected. Repeated
tool/query pairs within one turn reuse the existing result rather than making
another provider request. Native tool-call IDs and normalized arguments are
kept consistent in the scratchpad.

Duplicate-query prevention applies only within the current turn, not the entire
conversation. A new user request can perform a fresh lookup after an earlier
failure. If Qwen repeats the old generic Wolfram failure without having called
Wolfram in the current turn, the agent supplies corrective feedback rather than
saving it as another provider failure. Actual tool failures remain authoritative.

For Wolfram Alpha, set `WOLFRAM_ALPHA_APPID` in `LangChain/.env`. If it is missing,
the tool reports the setup error rather than making an unauthenticated request.
For example, the integral of `x^2` from `0` to `3` should return `9` using the
provider's result, not a `wolfram_alpha_search` call description.

Completed Wolfram-only calculations now return the tool's already-formatted
result (or its setup/error message) directly. They do not wait for a second
Ollama inference just to reword a computational answer. Other research workflows
retain their normal tool-and-answer flow.

### Wolfram requests (`12.py`)

The tool sends an HTTPS Full Results API request with `format=plaintext` and
`User-Agent: KnowledgeChatbot/1.0`. Paired live checks found that the default
HTTPX User-Agent received HTTP 403 while this application identity received
HTTP 200 XML using the same AppID and query. The header is not a replacement for
valid credentials or API access.

Response parsing and preferred-pod formatting otherwise follow `10.py`.
`raise_for_status()` runs before XML parsing, so a non-success HTTP response is
never accepted merely because its body says `success="true"`. HTTP and XML
parsing failures return the existing generic tool error; no automatic retry of
the same query is made in that turn.

HTTPX INFO logs include full query URLs. Disable those logs when using real
credentials, and rotate an AppID if it was exposed in publicly shared logs.

Reference: [Wolfram Full Results API](https://products.wolframalpha.com/api/documentation).

## Timeouts (`12.py`)

The current code uses a 30-second external HTTP-client timeout, a 60-second
Ollama HTTP-client timeout, and a 120-second agent deadline with at most 15
iterations. These are code settings, not environment-variable overrides.
There is no separate output-token budget in this `10.py`-based implementation.

Restart `python 12.py` after updating; `reload=False` means an existing server
does not load changes automatically. A fresh chat session can avoid unnecessary
model imitation of older responses without deleting saved conversations.

## Text-only operation (`12.py`)

The application accepts text messages and returns text or Markdown. Its six
research tools accept text queries and return text results. No device capture
or image, video, or audio processing is available.

Regression tests use deterministic model responses, HTTP transports, and cache
or database test fixtures. They do not use real `.env` credentials or contact
Ollama or external providers:

```powershell
.\.venv\Scripts\python.exe -B -m pytest LangChain/tests -q -p no:cacheprovider
```
