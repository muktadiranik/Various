import os
import asyncio
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from contextlib import asynccontextmanager

import xml.etree.ElementTree as ET
import uvicorn
import httpx
from dotenv import load_dotenv

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Knowledge Base Tools
import arxiv
import wikipedia
import redis

# Ollama & LangChain
import ollama
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun, PubmedQueryRun
from langchain_tavily import TavilySearch
from langchain_community.chat_message_histories import RedisChatMessageHistory

from sqlalchemy import Column, Integer, String, Text, DateTime, func, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

load_dotenv()

# ==========================================
# 1. Database & ORM Configuration
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/knowledge_database")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_database():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    role = Column(String(50), nullable=False)  # 'human' or 'ai'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)


# ==========================================
# 2. Pydantic Schemas
# ==========================================
class ChatMessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str = Field(..., description="Role of the speaker: 'human' or 'ai'")
    content: str
    timestamp: Optional[datetime] = None


class ConversationSummarySchema(BaseModel):
    session_id: str
    message_count: int
    last_updated: Optional[datetime] = None


class ConversationDetailSchema(BaseModel):
    session_id: str
    messages: List[ChatMessageSchema]


class PaginatedResponseMeta(BaseModel):
    total_items: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class PaginatedConversationSummary(BaseModel):
    meta: PaginatedResponseMeta
    data: List[ConversationSummarySchema]


class PaginatedConversationDetail(BaseModel):
    meta: PaginatedResponseMeta
    session_id: str
    messages: List[ChatMessageSchema]


class PaginatedGroupedConversations(BaseModel):
    meta: PaginatedResponseMeta
    data: dict[str, List[ChatMessageSchema]]


# Global Configs
wikipedia.set_user_agent("KnowledgeChatbot/1.0 (contact@yourdomain.com)")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
FLUSH_INTERVAL = 5  # Flush to Postgres every 5 message interactions
redis_client = redis.Redis.from_url(REDIS_URL)

PREFERRED_WOLFRAM_PODS: List[str] = [
    "Input interpretation", "Input", "Result", "Exact result",
    "Decimal approximation", "Solution", "Definite integral",
    "Indefinite integral", "Derivative", "Limit", "Value",
    "Conversions", "Scientific notation", "Expanded form", "Alternate form",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application starting up...")
    yield
    print("🛑 Application shutting down...")


app = FastAPI(
    title="Multi-Source Knowledge Chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ==========================================
# 3. Connection Manager
# ==========================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        if websocket not in self.active_connections:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
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
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("https://api.wolframalpha.com/v2/query", params=params)
            response.raise_for_status()

        root = ET.fromstring(response.text)
        if root.attrib.get("error") == "true" or root.attrib.get("success") != "true":
            return f"No computational results found for '{query}'. Do NOT retry this exact query."

        pod_map: Dict[str, List[str]] = {}
        for pod in root.findall("pod"):
            title = pod.attrib.get("title", "").strip()
            values = [
                subpod.findtext("plaintext").strip()
                for subpod in pod.findall("subpod")
                if subpod.findtext("plaintext") and subpod.findtext("plaintext").strip()
            ]
            if values and title:
                pod_map[title] = values

        collected: List[str] = []
        for preferred in PREFERRED_WOLFRAM_PODS:
            if preferred in pod_map:
                collected.append(f"### {preferred}\n" + "\n".join(pod_map[preferred]))
                del pod_map[preferred]

        if not collected:
            for title, values in pod_map.items():
                collected.append(f"### {title}\n" + "\n".join(values))

        return "\n\n---\n\n".join(collected)
    except Exception as e:
        return f"Wolfram Alpha search failed: {e}. Do NOT retry."


@tool
async def wikipedia_search(query: str) -> str:
    """Search Wikipedia for general knowledge, historical events, biographies, places, science, and technology."""
    try:
        page = await asyncio.to_thread(wikipedia.page, query, auto_suggest=True)
        return f"Title: {page.title}\n\nSummary: {page.summary[:1000]}\n\nURL: {page.url}"
    except Exception as e:
        return f"Wikipedia search failed for '{query}': {e}. Proceed without repeating this search."


@tool
async def arxiv_search(query: str) -> str:
    """Search arXiv for academic research papers."""
    try:
        def _fetch():
            client = arxiv.Client()
            search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
            return [
                f"Title: {paper.title}\nAuthors: {', '.join(a.name for a in paper.authors)}\nPublished: {paper.published.date()}\nSummary: {paper.summary[:600]}\nURL: {paper.entry_id}"
                for paper in client.results(search)
            ]
        papers = await asyncio.to_thread(_fetch)
        return "\n\n---\n\n".join(papers) if papers else f"No arXiv papers found for query '{query}'."
    except Exception as e:
        return f"ArXiv search failed: {e}"


pubmed_runner = PubmedQueryRun()

@tool
async def pubmed_search(query: str) -> str:
    """Search biomedical literature from PubMed for medicine, healthcare, biology, and clinical research."""
    try:
        result = await asyncio.to_thread(pubmed_runner.run, query)
        return result if result and result.strip() else f"No PubMed results found for '{query}'."
    except Exception as e:
        return f"PubMed search failed: {e}"


@tool
async def ollama_web_search(query: str) -> str:
    """Search the web using Ollama's native web search feature for real-time information."""
    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        return "OLLAMA_API_KEY is missing from environment variables."

    try:
        def _search():
            client = ollama.Client(
                host="https://ollama.com",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            return client.web_search(query)

        res = await asyncio.to_thread(_search)
        if isinstance(res, dict) and "results" in res:
            formatted = [
                f"Title: {item.get('title')}\nSummary: {item.get('snippet')}\nURL: {item.get('url')}"
                for item in res["results"]
            ]
            return "\n\n---\n\n".join(formatted) if formatted else f"No Ollama search results found for '{query}'."

        return str(res)
    except Exception as e:
        return f"Ollama web search failed: {e}"


duckduckgo_runner = DuckDuckGoSearchRun()

@tool
async def duckduckgo_search(query: str) -> str:
    """Search the web for real-time news, current events, programming, or quick factual searches."""
    try:
        res = await asyncio.to_thread(duckduckgo_runner.run, query)
        if not res or "No good DuckDuckGo Search Result" in str(res):
            return f"DuckDuckGo found no results for query '{query}'. Do NOT retry this search."
        return str(res)
    except Exception as e:
        return f"DuckDuckGo search failed: {e}"


tavily_runner = TavilySearch(max_results=3, search_depth="basic")

@tool
async def tavily_search(query: str) -> str:
    """Search the internet using Tavily for deep web research and real-time summaries."""
    try:
        res = await asyncio.to_thread(tavily_runner.run, query)
        return str(res) if res else f"No Tavily results found for query '{query}'."
    except Exception as e:
        return f"Tavily search failed: {e}"


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
llm = ChatOllama(
    base_url="https://ollama.com",
    model="gpt-oss:120b",
    temperature=0,
    headers={"Authorization": f"Bearer {os.environ.get('OLLAMA_API_KEY')}"},
    client_kwargs={"headers": {"Authorization": f"Bearer {os.environ.get('OLLAMA_API_KEY')}"}}
)

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

### Tool Selection Rules:
1. **Wolfram Alpha (`wolfram_alpha_search`)**:
   - Primary tool for exact calculations, mathematical equations, physics, chemistry, unit conversions, scientific constants, and exact data metrics.
   - Domain: Mathematics, calculus, algebra, differential equations, integrals, derivatives, physics, chemistry, engineering, astronomy, unit conversions, geography statistics.

2. **Wikipedia (`wikipedia_search`)**:
   - Primary tool for background context, historical events, biographies, geography, and general encyclopedia knowledge.
   - Domain: History, biographies, famous people, countries, general knowledge concepts.

3. **ArXiv (`arxiv_search`)**:
   - Primary tool for academic pre-prints and scientific research papers.
   - Domain: Artificial Intelligence, Machine Learning, Computer Science, Physics, and Mathematics research papers.

4. **PubMed (`pubmed_search`)**:
   - Primary tool for medical, healthcare, biomedical, and clinical research literature.
   - Domain: Medicine, diseases, healthcare, biology, clinical research.

5. **Ollama Web Search (`ollama_web_search`)**:
   - Primary tool for fast, real-time web lookups, current events, online news articles, and general web queries using Ollama's native search API.
   - Domain: Real-time information, current news, online references, quick web queries.

6. **DuckDuckGo (`duckduckgo_search`)**:
   - Fallback web search engine for technical documentation, programming troubleshooting, and general web browsing.
   - Domain: Programming questions, technical stack documentation, website lookups.

7. **Tavily Search (`tavily_search`)**:
   - Specialized search engine for deep, multi-page web retrieval and comprehensive web research summaries.
   - Domain: In-depth web research, complex multi-source web queries, comprehensive summaries.

### General & Formatting Rules:
- Always choose the most appropriate tool based on the user's domain instead of guessing.
- If multiple tools are required, call them sequentially.
- If no tool is needed (e.g., reasoning, explanations, code generation, writing, or general conversation), answer directly.

Examples:

- Python → ```python
- JavaScript → ```javascript
- TypeScript → ```typescript
- HTML → ```html
- CSS → ```css
- SCSS/SASS → ```scss
- JSON → ```json
- YAML → ```yaml
- TOML → ```toml
- XML → ```xml
- Markdown → ```markdown
- SQL → ```sql
- Bash/Shell → ```bash
- PowerShell → ```powershell
- Dockerfile → ```dockerfile
- Makefile → ```makefile
- Nginx → ```nginx
- Apache Config → ```apache
- INI → ```ini
- CSV → ```csv
- TSV → ```text
- Plain Text → ```text
- LaTeX → ```latex
- BibTeX → ```bibtex
- Mermaid → ```mermaid
- GraphQL → ```graphql
- Protocol Buffers → ```proto
- C → ```c
- C++ → ```cpp
- C# → ```csharp
- Java → ```java
- Kotlin → ```kotlin
- Swift → ```swift
- Go → ```go
- Rust → ```rust
- PHP → ```php
- Ruby → ```ruby
- Perl → ```perl
- Lua → ```lua
- R → ```r
- MATLAB → ```matlab
- Julia → ```julia
- Dart → ```dart
- Scala → ```scala
- Haskell → ```haskell
- Elixir → ```elixir
- Erlang → ```erlang
- Objective-C → ```objective-c
- Assembly → ```asm
- VB.NET → ```vbnet
- Solidity → ```solidity
- Terraform → ```terraform
- HCL → ```hcl
- Kubernetes YAML → ```yaml

### Multi-file Output
If the user requests multiple files:
- Clearly separate each file.
- Start each file with its filename as a Markdown heading.
- Then output the complete file inside the appropriate fenced code block.

Example:
## app.py

```python
...
```

## requirements.txt

```text
...
```

## docker-compose.yml

```yaml
...
```

### Unsupported Languages
If Markdown supports a language identifier, always use it.
If no official identifier exists, use:

```text
```

rather than outputting raw text.

### Completeness
- Return complete files unless the user explicitly requests only a partial snippet.
- Never omit imports, package declarations, namespaces, function signatures, comments, or configuration headers when they are required for a working file.
- Preserve proper indentation and formatting.
- Ensure generated files are syntactically valid.

### Markdown Safety
- Use Markdown code fences only for file or code output.
- Do not wrap ordinary conversational responses in code fences.
- Do not nest Markdown code fences inside other code fences.
- Do not wrap ordinary conversational responses in Markdown code fences.
""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=15,  
    handle_parsing_errors=True,
    early_stopping_method="generate",
    return_intermediate_steps=True,
)


def persist_messages_to_postgres(session_id: str, messages: list):
    """Flushes full message list into Postgres database synchronously within thread."""
    database = SessionLocal()
    try:
        database.query(ChatLog).filter(ChatLog.session_id == session_id).delete()

        database_records = []
        for message in messages:
            role = "human" if isinstance(message, HumanMessage) else "ai"
            database_records.append(
                ChatLog(session_id=session_id, role=role, content=message.content)
            )

        database.add_all(database_records)
        database.commit()
        print(f"✅ Successfully persisted {len(database_records)} messages to PostgreSQL for session: {session_id}")
    except Exception as err:
        database.rollback()
        print(f"❌ Failed to persist chat history to Postgres: {err}")
    finally:
        database.close()


# ==========================================
# 6. REST Endpoints
# ==========================================
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})


@app.get(
    "/conversations",
    response_model=PaginatedConversationSummary,
    tags=["Conversations"],
    summary="Get paginated summary of all conversation sessions"
)
async def get_all_conversations(
    limit: int = Query(20, ge=1, le=100, description="Number of sessions per page"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    database: Session = Depends(get_database)
):
    try:
        summary_query = (
            database.query(
                ChatLog.session_id,
                func.count(ChatLog.id).label("message_count"),
                func.max(ChatLog.timestamp).label("last_updated")
            )
            .group_by(ChatLog.session_id)
        )

        total_items = summary_query.count()

        results = (
            summary_query
            .order_by(func.max(ChatLog.timestamp).desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        items = [
            ConversationSummarySchema(
                session_id=row.session_id,
                message_count=row.message_count,
                last_updated=row.last_updated
            )
            for row in results
        ]

        return PaginatedConversationSummary(
            meta=PaginatedResponseMeta(
                total_items=total_items,
                limit=limit,
                offset=offset,
                has_next=(offset + limit) < total_items,
                has_previous=offset > 0,
            ),
            data=items
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conversation summaries: {str(e)}"
        )


@app.get(
    "/conversations/{session_id}",
    response_model=PaginatedConversationDetail,
    tags=["Conversations"],
    summary="Get paginated chat messages for a specific Session ID"
)
async def get_conversation_by_id(
    session_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of messages per page"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    database: Session = Depends(get_database)
):
    try:
        base_query = database.query(ChatLog).filter(ChatLog.session_id == session_id)
        total_items = base_query.count()

        if total_items == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with session_id '{session_id}' not found."
            )

        logs = (
            base_query
            .order_by(ChatLog.timestamp.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        messages = [ChatMessageSchema.model_validate(log) for log in logs]

        return PaginatedConversationDetail(
            meta=PaginatedResponseMeta(
                total_items=total_items,
                limit=limit,
                offset=offset,
                has_next=(offset + limit) < total_items,
                has_previous=offset > 0,
            ),
            session_id=session_id,
            messages=messages
        )

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conversation transcript: {str(e)}"
        )


@app.get(
    "/conversations/all/grouped",
    response_model=PaginatedGroupedConversations,
    tags=["Conversations"],
    summary="Get paginated sessions with all their raw conversations"
)
async def get_all_conversations_full(
    limit: int = Query(10, ge=1, le=50, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    database: Session = Depends(get_database)
):
    try:
        distinct_sessions_query = database.query(ChatLog.session_id).distinct()
        total_items = distinct_sessions_query.count()

        paginated_session_ids = [
            row[0] for row in distinct_sessions_query.offset(offset).limit(limit).all()
        ]

        if not paginated_session_ids:
            return PaginatedGroupedConversations(
                meta=PaginatedResponseMeta(
                    total_items=total_items,
                    limit=limit,
                    offset=offset,
                    has_next=False,
                    has_previous=offset > 0,
                ),
                data={}
            )

        logs = (
            database.query(ChatLog)
            .filter(ChatLog.session_id.in_(paginated_session_ids))
            .order_by(ChatLog.session_id, ChatLog.timestamp.asc())
            .all()
        )

        grouped: Dict[str, List[ChatMessageSchema]] = {sid: [] for sid in paginated_session_ids}
        for log in logs:
            grouped[log.session_id].append(ChatMessageSchema.model_validate(log))

        return PaginatedGroupedConversations(
            meta=PaginatedResponseMeta(
                total_items=total_items,
                limit=limit,
                offset=offset,
                has_next=(offset + limit) < total_items,
                has_previous=offset > 0,
            ),
            data=grouped
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch grouped conversations: {str(e)}"
        )


# ==========================================
# 7. WebSocket Gateway
# ==========================================
@app.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str = Query("default_session")
):
    await manager.connect(websocket)

    redis_history = RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=86400
    )

    try:
        while True:
            question = await websocket.receive_text()
            question = question.strip()

            if not question:
                continue

            try:
                current_messages = redis_history.messages

                result = await agent_executor.ainvoke(
                    {
                        "question": question,
                        "chat_history": current_messages,
                    }
                )

                answer = result.get("output", "Sorry, I couldn't find an answer.")

                # 1. Update Redis Chat Memory
                redis_history.add_user_message(question)
                redis_history.add_ai_message(answer)

                # 2. Check turn count in Redis
                counter_key = f"counter:{session_id}"
                turn_count = redis_client.incr(counter_key)

                # 3. Interval persistence trigger to PostgreSQL
                if turn_count % FLUSH_INTERVAL == 0:
                    updated_messages = redis_history.messages
                    await asyncio.to_thread(
                        persist_messages_to_postgres,
                        session_id,
                        updated_messages
                    )

                await manager.send_message(f"AI: {answer}", websocket)

            except Exception as agent_error:
                print(f"Agent Error: {agent_error}")
                await manager.send_message(
                    "AI: Sorry, an error occurred while processing your request.",
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as websocket_error:
        manager.disconnect(websocket)
        print(f"WebSocket Error: {websocket_error}")


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000, reload=False)