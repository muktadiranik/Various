import os
import asyncio
from typing import List, Dict
from contextlib import asynccontextmanager
import xml.etree.ElementTree as ET

import uvicorn
import httpx
from dotenv import load_dotenv

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ArXiv & Wikipedia
import arxiv
import wikipedia

# Ollama
import ollama

# LangChain
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun, PubmedQueryRun
from langchain_tavily import TavilySearch

wikipedia.set_user_agent("KnowledgeChatbot/1.0 (contact@yourdomain.com)")

load_dotenv()

MAX_CHAT_HISTORY = 10

PREFERRED_WOLFRAM_PODS: List[str] = [
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
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Clean lifespan manager (Playwright process setup removed)."""
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


"""
Asynchronous Tools (Non-blocking I/O)
"""


@tool
async def wolfram_alpha_search(query: str) -> str:
    """
    Search Wolfram Alpha for computational knowledge, mathematics, calculus, physics, chemistry, engineering, and unit conversions.
    """
    appid = os.getenv("WOLFRAM_ALPHA_APPID")

    if not appid:
        return (
            "Wolfram Alpha AppID is not configured. "
            "Please set WOLFRAM_ALPHA_APPID in your environment variables."
        )

    params = {
        "appid": appid,
        "input": query,
        "format": "plaintext",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.wolframalpha.com/v2/query", params=params
            )
            response.raise_for_status()

        root = ET.fromstring(response.text)

        if root.attrib.get("error") == "true":
            return "Wolfram Alpha returned an error processing the query."

        if root.attrib.get("success") != "true":
            return f"No computational results found for '{query}'."

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

        if not pod_map:
            return "No plaintext results returned by Wolfram Alpha."

        collected: List[str] = []

        for preferred in PREFERRED_WOLFRAM_PODS:
            if preferred in pod_map:
                collected.append(f"### {preferred}\n" +
                                 "\n".join(pod_map[preferred]))
                del pod_map[preferred]

        if not collected:
            for title, values in pod_map.items():
                collected.append(f"### {title}\n" + "\n".join(values))

        return "\n\n---\n\n".join(collected)

    except httpx.TimeoutException:
        return "Wolfram Alpha request timed out."
    except httpx.HTTPStatusError as e:
        return f"Wolfram Alpha HTTP error: {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Wolfram Alpha network request failed: {e}"
    except ET.ParseError:
        return "Failed to parse the XML response from Wolfram Alpha."
    except Exception as e:
        return f"Wolfram Alpha search failed: {e}"


@tool
async def wikipedia_search(query: str) -> str:
    """Search Wikipedia for general knowledge, historical events, biographies, places, science, and technology."""
    try:
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
async def ollama_web_search(query: str) -> str:
    """
    Search the web using Ollama's native web search feature for real-time information, 
    current events, and online articles.
    """
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

        # Format results into readable text if returns dict or object list
        if isinstance(res, dict) and "results" in res:
            formatted = []
            for item in res["results"]:
                title = item.get("title", "No Title")
                snippet = item.get("snippet", "")
                url = item.get("url", "")
                formatted.append(
                    f"Title: {title}\nSummary: {snippet}\nURL: {url}")
            return "\n\n---\n\n".join(formatted) if formatted else "No results found."

        return str(res)

    except Exception as e:
        return f"Ollama web search failed: {e}"


@tool
async def duckduckgo_search(query: str) -> str:
    """Search the web for real-time news, current events, programming, or quick factual searches."""
    try:
        return await asyncio.to_thread(duckduckgo_runner.run, query)
    except Exception as e:
        return f"DuckDuckGo search failed: {e}"


tavily_runner = TavilySearch(max_results=3, search_depth="basic")


@tool
async def tavily_search(query: str) -> str:
    """Search the internet using Tavily for deep web research and real-time summaries."""
    try:
        return await asyncio.to_thread(tavily_runner.run, query)
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


"""
LLM & Prompt
"""


llm = ChatOllama(
    base_url="https://ollama.com",
    model="gpt-oss:120b",
    temperature=0,
    headers={
        "Authorization": f"Bearer {os.environ.get('OLLAMA_API_KEY')}"
    },
    client_kwargs={
        "headers": {
            "Authorization": f"Bearer {os.environ.get('OLLAMA_API_KEY')}"
        }
    }
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an advanced AI research assistant with access to specialized knowledge bases and web search engines.

### Tool Selection Rules:

1. **Wolfram Alpha (`wolfram_alpha_search`)**:
   - Primary tool for exact calculations, mathematical equations, physics, chemistry, unit conversions, scientific constants, and exact data metrics.
   - mathematics
   - calculus
   - algebra
   - differential equations
   - integrals
   - derivatives
   - physics
   - chemistry
   - engineering
   - astronomy
   - unit conversions
   - scientific constants
   - geography statistics

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

5. **Ollama Web Search (`ollama_web_search`)**:
   - Primary tool for live internet searches, recent news, real-time facts, tech stack documentation, and general web browsing.
   - Use for quick real-time web lookups, current news, and general online references.
   - recent news
   - real-time information
   - current events
   - online articles
   - quick web searches

6. **DuckDuckGo (`duckduckgo_search`)**:
   - Use for live internet searches, recent news, real-time facts, tech stack documentation, and general web browsing.
   - recent news
   - websites
   - current events
   - programming questions
   - quick web searches

7. **Tavily Search (`tavily_search`)**:
   - Use for complex web retrieval queries requiring deep content summaries from real-time web pages.
   - deep web research
   - comprehensive summaries
   - recent online information
   - multiple web pages

7. **Ollama Web Search (`ollama_web_search`)**:
   - Primary tool for running searches directly through Ollama's web search client.
   - Use for quick real-time web lookups, current news, and general online references.
   - real-time information
   - current events
   - online articles

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
    return_intermediate_steps=True,
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
    uvicorn.run(app=app, host="0.0.0.0", port=8000, reload=False)
