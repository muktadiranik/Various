import os
import asyncio
from typing import List

import uvicorn
import httpx
from dotenv import load_dotenv

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ArXiv & Wikipedia
import arxiv
import wikipedia

# LangChain
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun, PubmedQueryRun
from langchain_tavily import TavilySearch

wikipedia.set_user_agent("WikipediaChatbot/1.0 (contact@example.com)")

# Reduced to 6 messages (3 turns) for lower context overhead
MAX_CHAT_HISTORY = 6

load_dotenv()

app = FastAPI(title="Multi-Source Knowledge Chatbot", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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


# -------------------------------------------------------
# Asynchronous Tools (Non-blocking I/O)
# -------------------------------------------------------

@tool
async def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for general knowledge, historical events,
    biographies, places, science, and technology.
    """
    try:
        # Offload sync wikipedia library call to threadpool
        page = await asyncio.to_thread(wikipedia.page, query, auto_suggest=True)
        return f"Title: {page.title}\n\nSummary: {page.summary[:1000]}\n\nURL: {page.url}"
    except wikipedia.DisambiguationError as e:
        return f"Multiple matching pages found: {', '.join(e.options[:5])}"
    except wikipedia.PageError:
        return "No Wikipedia page found."
    except Exception as e:
        return f"Wikipedia search failed: {e}"


@tool
async def arxiv_search(query: str) -> str:
    """Search arXiv for academic research papers."""
    try:
        def _fetch():
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=2,  # Reduced from 3 to save context tokens
                sort_by=arxiv.SortCriterion.Relevance,
            )
            return [
                f"Title: {paper.title}\nAuthors: {', '.join(a.name for a in paper.authors)}\nPublished: {paper.published.date()}\nSummary: {paper.summary[:600]}\nURL: {paper.entry_id}"
                for paper in client.results(search)
            ]

        papers = await asyncio.to_thread(_fetch)
        return "\n\n---\n\n".join(papers) if papers else "No papers found."
    except Exception as e:
        return f"ArXiv search failed: {e}"


pubmed_runner = PubmedQueryRun()


@tool
async def pubmed_search(query: str) -> str:
    """Search biomedical literature from PubMed for medicine, healthcare, biology, and clinical research."""
    try:
        result = await asyncio.to_thread(pubmed_runner.run, query)
        return result if result.strip() else "No PubMed results found."
    except Exception as e:
        return f"PubMed search failed: {e}"


duckduckgo_runner = DuckDuckGoSearchRun()


@tool
async def duckduckgo_search(query: str) -> str:
    """Search the web for real-time news, current events, programming, or quick factual searches."""
    try:
        return await asyncio.to_thread(duckduckgo_runner.run, query)
    except Exception as e:
        return f"DuckDuckGo search failed: {e}"


tavily_tool = None
if os.getenv("TAVILY_API_KEY"):
    tavily_runner = TavilySearch(max_results=3, search_depth="basic")

    @tool
    async def tavily_search(query: str) -> str:
        """Search the internet using Tavily for deep web research and real-time summaries."""
        try:
            return await asyncio.to_thread(tavily_runner.run, query)
        except Exception as e:
            return f"Tavily search failed: {e}"

    tavily_tool = tavily_search

tools = [wikipedia_search, arxiv_search, pubmed_search, duckduckgo_search]
if tavily_tool:
    tools.append(tavily_tool)


# -------------------------------------------------------
# LLM & Lightweight Prompt
# -------------------------------------------------------

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
    num_ctx=4096,  # Reduced context limit to speed up KV cache processing
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an advanced AI research assistant with access to specialized tools.

### Tool Guidelines:
- **Wikipedia (`wikipedia_search`)**: History, biographies, general encyclopedia concepts.
- **ArXiv (`arxiv_search`)**: Computer Science, AI, Math, Physics pre-prints.
- **PubMed (`pubmed_search`)**: Biomedical, medical, and clinical research.
- **DuckDuckGo (`duckduckgo_search`)**: Quick web lookups, current events, news.
- **Tavily (`tavily_search`)**: Deep web retrieval and live web pages.

### Rules:
- Call tools sequentially only when necessary. If no tool is needed, answer directly.
- Whenever returning code, scripts, markup, configuration files, or structured data (JSON, CSV, SQL, etc.), ALWAYS enclose the entire output inside markdown code fences with a language tag (e.g., ```python ... ```). Never output plain code/file contents outside code fences.""",
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
    verbose=True,              # Set to False in production to avoid console I/O slowdowns
    max_iterations=3,          # Cap tool execution iterations to 3
    max_execution_time=15.0,   # Set 15s timeout limit
    handle_parsing_errors=True,
    return_intermediate_steps=False,
)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    chat_history = []

    try:
        while True:
            question = await websocket.receive_text()
            question = question.strip()

            if not question:
                continue

            try:
                result = await agent_executor.ainvoke(
                    {
                        "question": question,
                        "chat_history": chat_history,
                    }
                )

                answer = result.get(
                    "output", "Sorry, I couldn't find an answer.")

                chat_history.append(HumanMessage(content=question))
                chat_history.append(AIMessage(content=answer))

                # Maintain strict sliding memory window
                if len(chat_history) > MAX_CHAT_HISTORY:
                    chat_history = chat_history[-MAX_CHAT_HISTORY:]

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
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
