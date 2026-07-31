import os
import asyncio
from typing import List, Optional
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ArXiv & Wikipedia
import arxiv
import wikipedia

# LangChain
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun, PubmedQueryRun
from langchain_tavily import TavilySearch

# BeautifulSoup
from bs4 import BeautifulSoup

# Playwright
from playwright.async_api import async_playwright, Browser, Playwright

wikipedia.set_user_agent("WikipediaChatbot/1.0 (contact@example.com)")

MAX_CHAT_HISTORY = 10
load_dotenv()

app = FastAPI(title="Multi-Source Knowledge Chatbot", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global references for Playwright and Browser objects
playwright_instance: Optional[Playwright] = None
browser_instance: Optional[Browser] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Manager:
    Launches a shared Playwright Chromium browser on startup
    and closes it when the application shuts down.
    """
    global playwright_instance, browser_instance

    print("🚀 Starting global Playwright browser instance...")
    playwright_instance = await async_playwright().start()
    browser_instance = await playwright_instance.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",  # Helps prevent memory issues in docker/linux
        ]
    )

    yield  # Application runs while suspended here

    print("🛑 Closing global Playwright browser instance...")
    if browser_instance:
        await browser_instance.close()
    if playwright_instance:
        await playwright_instance.stop()


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
                max_results=3,
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


@tool
async def google_playwright_search(query: str) -> str:
    """
    Search Google using a shared headless browser context.
    Provides fast, real-time web news and snippets without external API keys.
    """
    global browser_instance

    if not browser_instance or not browser_instance.is_connected():
        return "Browser instance is not available."

    context = None
    try:
        # Create an isolated context (like an Incognito window)
        context = await browser_instance.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        page = await context.new_page()

        # Block heavy media assets to speed up page load & save bandwidth
        await page.route(
            "**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}",
            lambda route: route.abort()
        )

        # Navigate to Google Search
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=8000)

        # Extract page HTML
        html = await page.content()

        # Parse Google Search Result DOM with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for g in soup.select("div.g")[:4]:
            title_el = g.select_one("h3")
            link_el = g.select_one("a")
            snippet_el = g.select_one("div.VwiC3b, div.IsZvec")

            if title_el and link_el:
                title = title_el.get_text(strip=True)
                url = link_el.get("href", "")
                snippet = snippet_el.get_text(
                    strip=True) if snippet_el else "No snippet available."

                if url.startswith("http"):
                    results.append(
                        f"Title: {title}\nURL: {url}\nSnippet: {snippet}")

        if not results:
            return "No organic Google results found or query was blocked by CAPTCHA."

        return "\n\n---\n\n".join(results)

    except Exception as e:
        return f"Playwright Google search failed: {e}"

    finally:
        # Always close the context to free memory/tabs, leaving the main browser active
        if context:
            await context.close()

tools = [wikipedia_search, arxiv_search, pubmed_search,
         duckduckgo_search, google_playwright_search]
if tavily_tool:
    tools.append(tavily_tool)


# -------------------------------------------------------
# LLM & Prompt
# -------------------------------------------------------

llm = ChatOllama(
    model="qwen2.5-coder:3b",
    temperature=0,
    num_ctx=8192,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an advanced AI research assistant with access to specialized knowledge bases and web search engines.

### Tool Selection Rules:

1. **Google Search (`google_playwright_search`)**:
   - Primary tool for live internet searches, recent news, real-time facts, tech stack documentation, and general web browsing.
   - recent news
   - websites
   - current events
   - programming questions
   - quick web searches

2. **Wikipedia (`wikipedia_search`)**:
   - Primary tool for encyclopedia knowledge, historical events, biographies, geography, and foundational concepts.
   - general knowledge
   - history
   - biographies
   - geography
   - famous people
   - countries
   - encyclopedia information

3. **ArXiv (`arxiv_search`)**:
   - Use exclusively for academic pre-prints in AI, ML, Computer Science, Physics, and Mathematics research papers.
   - Artificial Intelligence
   - Machine Learning
   - Computer Science
   - Mathematics
   - Physics
   - scientific papers

4. **PubMed (`pubmed_search`)**:
   - Use for medical, healthcare, biomedical, and clinical research literature.
   - medicine
   - diseases
   - healthcare
   - biology
   - clinical research
   - biomedical literature

5. **DuckDuckGo (`duckduckgo_search`)**:
   - Secondary fallback web search tool if Google search yields no results or fails.
   - recent news
   - websites
   - current events
   - programming questions
   - quick web searches

6. **Tavily Search (`tavily_search`)**:
   - Use for complex web retrieval queries requiring deep content summaries from real-time web pages.
   - deep web research
   - comprehensive summaries
   - recent online information
   - multiple web pages

### General & Formatting Rules:

- Always choose the most appropriate tool based on the user's domain instead of guessing.
- If multiple tools are required, call them sequentially.
- If no tool is needed (e.g., reasoning, explanations, code generation, writing, or general conversation), answer directly.

### Output Formatting Rules

- Always detect the type of content the user is requesting and format it appropriately.
- Whenever the output represents a complete file, document, configuration, script, template, or structured content, wrap the entire output inside a properly labeled Markdown code fence.
- Never output complete files or structured content as raw text.

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
    max_iterations=5,
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
