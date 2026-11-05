import asyncio
import json
import logging
import os
import xml.etree.ElementTree as ET
from contextlib import AsyncExitStack, asynccontextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Iterator

import arxiv
import httpx
import ollama
import uvicorn
import wikipedia
from anyio import CancelScope
from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools import DuckDuckGoSearchRun, PubmedQueryRun
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    message_to_dict,
    messages_from_dict,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_tavily import TavilySearch
from pydantic import BaseModel, ConfigDict, Field
from redis.asyncio import Redis
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
logger = logging.getLogger(__name__)

# ==========================================
# 1. Database & ORM Configuration
# ==========================================
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/knowledge_database"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_database() -> Iterator[Session]:
    with SessionLocal() as database:
        yield database


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    role = Column(String(50), nullable=False)  # 'human' or 'ai'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ==========================================
# 2. Pydantic Schemas
# ==========================================
class ChatMessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str = Field(..., description="Role of the speaker: 'human' or 'ai'")
    content: str
    timestamp: datetime | None = None


class ConversationSummarySchema(BaseModel):
    session_id: str
    message_count: int
    last_updated: datetime | None = None


class ConversationDetailSchema(BaseModel):
    session_id: str
    messages: list[ChatMessageSchema]


class PaginatedResponseMeta(BaseModel):
    total_items: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool

    @classmethod
    def for_page(
        cls, total_items: int, limit: int, offset: int
    ) -> "PaginatedResponseMeta":
        return cls(
            total_items=total_items,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total_items,
            has_previous=offset > 0,
        )


class PaginatedConversationSummary(BaseModel):
    meta: PaginatedResponseMeta
    data: list[ConversationSummarySchema]


class PaginatedConversationDetail(BaseModel):
    meta: PaginatedResponseMeta
    session_id: str
    messages: list[ChatMessageSchema]


class PaginatedGroupedConversations(BaseModel):
    meta: PaginatedResponseMeta
    data: dict[str, list[ChatMessageSchema]]


# Global Configs
wikipedia.set_user_agent("KnowledgeChatbot/1.0 (contact@yourdomain.com)")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
FLUSH_INTERVAL = 5  # Flush to Postgres every 5 message interactions
HISTORY_TTL = 86400
AGENT_TIMEOUT = 120
RESULT_SEPARATOR = "\n\n---\n\n"

PREFERRED_WOLFRAM_PODS = (
    "Input interpretation",
    "Input",
    "Result",
    "Exact result",
    "Decimal approximation",
    "Solution",
    "Definite integral",
    "Indefinite integral",
    "Derivative",
    "Limit",
    "Value",
    "Conversions",
    "Scientific notation",
    "Expanded form",
    "Alternate form",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    try:
        await asyncio.to_thread(Base.metadata.create_all, bind=engine)
        async with AsyncExitStack() as stack:
            app.state.http_client = await stack.enter_async_context(
                httpx.AsyncClient(timeout=30.0)
            )
            app.state.redis = await stack.enter_async_context(
                Redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
            )
            api_key = os.getenv("OLLAMA_API_KEY")
            app.state.ollama_search = ollama.AsyncClient(
                host="https://ollama.com",
                headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
                timeout=30.0,
            )
            stack.push_async_callback(app.state.ollama_search.close)
            yield
    finally:
        await asyncio.to_thread(engine.dispose)
        logger.info("Application stopped")


app = FastAPI(
    title="Multi-Source Knowledge Chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ==========================================
# 3. Connection Manager
# ==========================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()
        self._session_locks: dict[str, asyncio.Lock] = {}
        self._session_connections: dict[str, int] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        self._session_connections[session_id] = (
            self._session_connections.get(session_id, 0) + 1
        )
        self._session_locks.setdefault(session_id, asyncio.Lock())

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        if websocket not in self.active_connections:
            return
        self.active_connections.discard(websocket)
        self._session_connections[session_id] -= 1
        if not self._session_connections[session_id]:
            del self._session_connections[session_id]
            del self._session_locks[session_id]

    def session_lock(self, session_id: str) -> asyncio.Lock:
        """Serialize turns for a session within this application worker."""
        return self._session_locks[session_id]

    async def send_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)


manager = ConnectionManager()


# ==========================================
# 4. Asynchronous Tools (Strict Output Formatted)
# ==========================================
@tool
async def wolfram_alpha_search(query: str) -> str:
    """Search Wolfram Alpha for computational knowledge, mathematics, calculus, physics, chemistry, engineering, and unit conversions."""
    appid = os.getenv("WOLFRAM_ALPHA_APPID")
    if not appid:
        return "Wolfram Alpha AppID is not configured."

    params = {"appid": appid, "input": query, "format": "plaintext"}

    try:
        response = await app.state.http_client.get(
            "https://api.wolframalpha.com/v2/query", params=params
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)
        if root.attrib.get("error") == "true" or root.attrib.get("success") != "true":
            return f"No computational results found for '{query}'. Do NOT retry this exact query."

        pod_map: dict[str, list[str]] = {}
        for pod in root.findall("pod"):
            title = pod.attrib.get("title", "").strip()
            values = [
                text
                for subpod in pod.findall("subpod")
                if (text := (subpod.findtext("plaintext") or "").strip())
            ]
            if values and title:
                pod_map[title] = values

        collected: list[str] = []
        for preferred in PREFERRED_WOLFRAM_PODS:
            if values := pod_map.pop(preferred, None):
                collected.append(f"### {preferred}\n" + "\n".join(values))

        if not collected:
            for title, values in pod_map.items():
                collected.append(f"### {title}\n" + "\n".join(values))

        return (
            RESULT_SEPARATOR.join(collected)
            or f"No computational results found for '{query}'."
        )
    except (httpx.HTTPError, ET.ParseError):
        logger.warning("Wolfram Alpha search failed")
        return "Wolfram Alpha search failed. Do NOT retry this query."


@tool
async def wikipedia_search(query: str) -> str:
    """Search Wikipedia for general knowledge, historical events, biographies, places, science, and technology."""
    try:

        def _fetch() -> str:
            # WikipediaPage properties may make additional synchronous HTTP requests.
            page = wikipedia.page(query, auto_suggest=True)
            return f"Title: {page.title}\n\nSummary: {page.summary[:1000]}\n\nURL: {page.url}"

        return await asyncio.to_thread(_fetch)
    except Exception:
        logger.warning("Wikipedia search failed")
        return f"Wikipedia search failed for '{query}'. Proceed without repeating this search."


@tool
async def arxiv_search(query: str) -> str:
    """Search arXiv for academic research papers."""
    try:

        def _fetch():
            client = arxiv.Client()
            search = arxiv.Search(
                query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance
            )
            return [
                f"Title: {paper.title}\nAuthors: {', '.join(a.name for a in paper.authors)}\nPublished: {paper.published.date()}\nSummary: {paper.summary[:600]}\nURL: {paper.entry_id}"
                for paper in client.results(search)
            ]

        papers = await asyncio.to_thread(_fetch)
        return (
            RESULT_SEPARATOR.join(papers)
            if papers
            else f"No arXiv papers found for query '{query}'."
        )
    except Exception:
        logger.warning("ArXiv search failed")
        return "ArXiv search failed. Do NOT retry this query."


pubmed_runner = PubmedQueryRun()


@tool
async def pubmed_search(query: str) -> str:
    """Search biomedical literature from PubMed for medicine, healthcare, biology, and clinical research."""
    try:
        result = await asyncio.to_thread(pubmed_runner.run, query)
        return (
            result
            if result and result.strip()
            else f"No PubMed results found for '{query}'."
        )
    except Exception:
        logger.warning("PubMed search failed")
        return "PubMed search failed. Do NOT retry this query."


@tool
async def ollama_web_search(query: str) -> str:
    """Search the web using Ollama's native web search feature for real-time information."""
    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        return "OLLAMA_API_KEY is missing from environment variables."

    try:
        response = await app.state.ollama_search.web_search(query)
        formatted = [
            f"Title: {item.title or ''}\nSummary: {item.content or ''}\nURL: {item.url or ''}"
            for item in response.results
        ]
        return (
            RESULT_SEPARATOR.join(formatted)
            or f"No Ollama search results found for '{query}'."
        )
    except Exception:
        logger.warning("Ollama web search failed")
        return "Ollama web search failed. Do NOT retry this query."


duckduckgo_runner = DuckDuckGoSearchRun()


@tool
async def duckduckgo_search(query: str) -> str:
    """Search the web for real-time news, current events, programming, or quick factual searches."""
    try:
        res = await asyncio.to_thread(duckduckgo_runner.run, query)
        if not res or "No good DuckDuckGo Search Result" in str(res):
            return f"DuckDuckGo found no results for query '{query}'. Do NOT retry this search."
        return str(res)
    except Exception:
        logger.warning("DuckDuckGo search failed")
        return "DuckDuckGo search failed. Do NOT retry this query."


@lru_cache(maxsize=1)
def get_tavily_runner() -> TavilySearch:
    # An optional provider must not prevent the entire app from importing.
    return TavilySearch(max_results=3, search_depth="basic")


@tool
async def tavily_search(query: str) -> str:
    """Search the internet using Tavily for deep web research and real-time summaries."""
    if not os.getenv("TAVILY_API_KEY"):
        return "TAVILY_API_KEY is missing from environment variables."
    try:
        res = await get_tavily_runner().ainvoke({"query": query})
        return (
            json.dumps(res, default=str)
            if res
            else f"No Tavily results found for query '{query}'."
        )
    except Exception:
        logger.warning("Tavily search failed")
        return "Tavily search failed. Do NOT retry this query."


tools = [
    wolfram_alpha_search,
    wikipedia_search,
    arxiv_search,
    pubmed_search,
    ollama_web_search,
    duckduckgo_search,
    tavily_search,
]


# ==========================================
# 5. Model, Guardrail Prompts, & Agent
# ==========================================
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an advanced AI research assistant with access to specialized knowledge bases and web search engines.

### STRICT ANTI-LOOPING & TOOL RULES:
1. NEVER invoke any tool with the exact same search query more than ONCE per conversation.
2. If a tool returns no results, an error, or insufficient data, DO NOT retry the exact same query. Formulate a totally different query or answer using available context.
3. Once you receive tool results, immediately synthesize your answer for the user. Do not make redundant search calls.

### Tool Selection Matrix:
- **Wolfram Alpha (`wolfram_alpha_search`)**: Exact math, calculations, physics, unit conversions.
- **Wikipedia (`wikipedia_search`)**: Background context, history, biographies, general knowledge.
- **ArXiv (`arxiv_search`)**: Scientific papers, ML/AI pre-prints.
- **PubMed (`pubmed_search`)**: Biomedical, medical, clinical literature.
- **Ollama Web Search (`ollama_web_search`)**: Fast, real-time web lookups and breaking news.
- **DuckDuckGo (`duckduckgo_search`)**: Programming docs, technical questions, quick lookups.
- **Tavily Search (`tavily_search`)**: Comprehensive, deep web research.

### General & Formatting Rules:
- Always choose the most appropriate tool based on the user's domain instead of guessing.
- If multiple tools are required, call them sequentially.
- If no tool is needed (e.g., reasoning, explanations, code generation, writing, or general conversation), answer directly.

### Multi-file Output
If the user requests multiple files:
- Clearly separate each file.
- Start each file with its filename as a Markdown heading.
- Then output the complete file inside the appropriate fenced code block.

### Unsupported Languages
Always label code fences with the appropriate language identifier (e.g. python,
javascript, json, sql, bash). Use text if no supported identifier exists.

### Completeness
- Return complete files unless the user explicitly requests only a partial snippet.
- Never omit imports, package declarations, namespaces, function signatures, comments, or configuration headers when they are required for a working file.
- Preserve proper indentation and formatting.
- Ensure generated files are syntactically valid.

### Markdown Safety
- Use Markdown code fences only for file or code output.
- Do not wrap ordinary conversational responses in code fences.
- Do not nest Markdown code fences inside other code fences.
""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


@lru_cache(maxsize=1)
def get_agent_executor() -> AgentExecutor:
    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        raise RuntimeError("OLLAMA_API_KEY is not configured")
    llm = ChatOllama(
        base_url="https://ollama.com",
        model="gpt-oss:120b",
        temperature=0,
        client_kwargs={
            "headers": {"Authorization": f"Bearer {api_key}"},
            "timeout": 60.0,
        },
    )
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=15,
        max_execution_time=AGENT_TIMEOUT,
        handle_parsing_errors=True,
        # Tool-calling agents do not implement the "generate" stopping method.
        early_stopping_method="force",
    )


def persist_messages_to_postgres(session_id: str, messages: list[BaseMessage]) -> None:
    """Append only unsaved messages; never delete an existing transcript."""
    with SessionLocal.begin() as database:
        saved = (
            database.query(ChatLog.role, ChatLog.content)
            .filter(ChatLog.session_id == session_id)
            .order_by(ChatLog.timestamp, ChatLog.id)
            .all()
        )
        transcript = [(message.type, message.content) for message in messages]
        if any(role not in {"human", "ai"} for role, _ in transcript):
            raise ValueError("Only human and AI messages can be persisted")
        if list(saved) != transcript[: len(saved)]:
            raise ValueError(
                "Cached history does not match the saved transcript")

        database.add_all(
            ChatLog(
                session_id=session_id,
                role=message.type,
                content=message.content,
            )
            for message in messages[len(saved):]
        )


def load_persisted_messages(session_id: str) -> list[BaseMessage]:
    with SessionLocal() as database:
        logs = (
            database.query(ChatLog)
            .filter(ChatLog.session_id == session_id)
            .order_by(ChatLog.timestamp, ChatLog.id)
            .all()
        )
        return [
            (HumanMessage if log.role == "human" else AIMessage)(
                content=log.content,
            )
            for log in logs
        ]


async def load_chat_history(session_id: str) -> list[BaseMessage]:
    """Keep the existing RedisChatMessageHistory key and serialization format."""
    redis_client = app.state.redis
    history_key = f"message_store:{session_id}"
    items = await redis_client.lrange(history_key, 0, -1)
    if items:
        return messages_from_dict([json.loads(item) for item in reversed(items)])

    messages = await asyncio.to_thread(load_persisted_messages, session_id)
    if messages:
        async with redis_client.pipeline(transaction=True) as pipeline:
            pipeline.lpush(
                history_key, *(json.dumps(message_to_dict(m))
                               for m in messages)
            )
            pipeline.expire(history_key, HISTORY_TTL)
            await pipeline.execute()
    return messages


async def store_chat_turn(session_id: str, messages: list[BaseMessage]) -> int:
    """Atomically save both messages, increment the turn count, and refresh TTLs."""
    history_key = f"message_store:{session_id}"
    counter_key = f"counter:{session_id}"
    async with app.state.redis.pipeline(transaction=True) as pipeline:
        pipeline.lpush(history_key, *(json.dumps(message_to_dict(m))
                       for m in messages))
        pipeline.expire(history_key, HISTORY_TTL)
        pipeline.incr(counter_key)
        pipeline.expire(counter_key, HISTORY_TTL)
        results = await pipeline.execute()
    return int(results[2])


async def flush_chat_history(session_id: str, messages: list[BaseMessage]) -> bool:
    try:
        # A cancelled await cannot stop a running thread. Wait for the transaction
        # before releasing the session lock or attempting another flush.
        with CancelScope(shield=True):
            await asyncio.to_thread(persist_messages_to_postgres, session_id, messages)
        return True
    except (SQLAlchemyError, ValueError):
        logger.exception("Failed to persist chat history")
        return False


# ==========================================
# 6. REST Endpoints
# ==========================================
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"request": request}
    )


@app.get(
    "/conversations",
    response_model=PaginatedConversationSummary,
    tags=["Conversations"],
    summary="Get paginated summary of all conversation sessions",
)
def get_all_conversations(
    limit: int = Query(
        20, ge=1, le=100, description="Number of sessions per page"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    database: Session = Depends(get_database),
):
    try:
        summary_query = database.query(
            ChatLog.session_id,
            func.count(ChatLog.id).label("message_count"),
            func.max(ChatLog.timestamp).label("last_updated"),
        ).group_by(ChatLog.session_id)

        total_items = (
            database.query(func.count(func.distinct(
                ChatLog.session_id))).scalar() or 0
        )

        results = (
            summary_query.order_by(
                func.max(ChatLog.timestamp).desc(), ChatLog.session_id
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

        items = [
            ConversationSummarySchema(
                session_id=row.session_id,
                message_count=row.message_count,
                last_updated=row.last_updated,
            )
            for row in results
        ]

        return PaginatedConversationSummary(
            meta=PaginatedResponseMeta.for_page(total_items, limit, offset), data=items
        )

    except SQLAlchemyError as e:
        logger.exception("Failed to fetch conversation summaries")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversation summaries.",
        ) from e


@app.get(
    "/conversations/{session_id}",
    response_model=PaginatedConversationDetail,
    tags=["Conversations"],
    summary="Get paginated chat messages for a specific Session ID",
)
def get_conversation_by_id(
    session_id: str,
    limit: int = Query(
        50, ge=1, le=200, description="Number of messages per page"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    database: Session = Depends(get_database),
):
    try:
        base_query = database.query(ChatLog).filter(
            ChatLog.session_id == session_id)
        total_items = base_query.count()

        if total_items == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with session_id '{session_id}' not found.",
            )

        logs = (
            base_query.order_by(ChatLog.timestamp.asc(), ChatLog.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        messages = [ChatMessageSchema.model_validate(log) for log in logs]

        return PaginatedConversationDetail(
            meta=PaginatedResponseMeta.for_page(total_items, limit, offset),
            session_id=session_id,
            messages=messages,
        )

    except SQLAlchemyError as e:
        logger.exception("Failed to fetch conversation transcript")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversation transcript.",
        ) from e


@app.get(
    "/conversations/all/grouped",
    response_model=PaginatedGroupedConversations,
    tags=["Conversations"],
    summary="Get paginated sessions with all their raw conversations",
)
def get_all_conversations_full(
    limit: int = Query(
        10, ge=1, le=50, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    database: Session = Depends(get_database),
):
    try:
        distinct_sessions_query = database.query(ChatLog.session_id).distinct()
        total_items = distinct_sessions_query.count()

        paginated_session_ids = [
            row[0]
            for row in distinct_sessions_query.order_by(ChatLog.session_id)
            .offset(offset)
            .limit(limit)
            .all()
        ]

        if not paginated_session_ids:
            return PaginatedGroupedConversations(
                meta=PaginatedResponseMeta.for_page(total_items, limit, offset), data={}
            )

        logs = (
            database.query(ChatLog)
            .filter(ChatLog.session_id.in_(paginated_session_ids))
            .order_by(ChatLog.session_id, ChatLog.timestamp.asc(), ChatLog.id.asc())
            .all()
        )

        grouped: dict[str, list[ChatMessageSchema]] = {
            sid: [] for sid in paginated_session_ids
        }
        for log in logs:
            grouped[log.session_id].append(
                ChatMessageSchema.model_validate(log))

        return PaginatedGroupedConversations(
            meta=PaginatedResponseMeta.for_page(total_items, limit, offset),
            data=grouped,
        )

    except SQLAlchemyError as e:
        logger.exception("Failed to fetch grouped conversations")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch grouped conversations.",
        ) from e


# ==========================================
# 7. WebSocket Gateway
# ==========================================
@app.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str = Query("default_session", min_length=1, max_length=255),
):
    await manager.connect(websocket, session_id)
    messages: list[BaseMessage] = []
    pending_flush = False

    try:
        while True:
            question = (await websocket.receive_text()).strip()

            if not question:
                continue

            try:
                async with manager.session_lock(session_id):
                    messages = await load_chat_history(session_id)
                    async with asyncio.timeout(AGENT_TIMEOUT):
                        result = await get_agent_executor().ainvoke(
                            {"question": question, "chat_history": messages}
                        )
                    answer = result.get(
                        "output") or "Sorry, I couldn't find an answer."
                    if not isinstance(answer, str):
                        answer = json.dumps(answer, default=str)

                    turn = [
                        HumanMessage(content=question),
                        AIMessage(content=answer),
                    ]
                    turn_count = await store_chat_turn(session_id, turn)
                    messages = [*messages, *turn]
                    pending_flush = True
                    if turn_count % FLUSH_INTERVAL == 0:
                        pending_flush = not await flush_chat_history(
                            session_id, messages
                        )

                await manager.send_message(f"AI: {answer}", websocket)

            except WebSocketDisconnect:
                raise
            except Exception:
                logger.exception("Failed to process chat request")
                await manager.send_message(
                    "AI: Sorry, an error occurred while processing your request.",
                    websocket,
                )

    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error")
    finally:
        try:
            # ASGI cancellation must not interrupt a final database transaction.
            with CancelScope(shield=True):
                if pending_flush:
                    async with manager.session_lock(session_id):
                        # Re-read to include turns completed by another connection.
                        try:
                            latest_messages = await load_chat_history(session_id)
                        except Exception:
                            logger.warning(
                                "Redis unavailable during final history flush"
                            )
                            latest_messages = messages
                        if len(latest_messages) < len(messages):
                            latest_messages = messages
                        await flush_chat_history(
                            session_id, latest_messages or messages
                        )
        finally:
            manager.disconnect(websocket, session_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app=app, host="0.0.0.0", port=8000, reload=False)
