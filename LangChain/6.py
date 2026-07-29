import os
from typing import List

import uvicorn
from dotenv import load_dotenv

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# LangChain
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.tools import tool

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

# Community Tools
from langchain_community.tools import (
    ArxivQueryRun,
    DuckDuckGoSearchRun,
    PubmedQueryRun,
    WikipediaQueryRun,
)

from langchain_community.tools.wolfram_alpha import (
    WolframAlphaQueryRun,
)

from langchain_community.utilities import (
    WikipediaAPIWrapper,
    ArxivAPIWrapper,
    WolframAlphaAPIWrapper,
)

from langchain_tavily import TavilySearch

import wikipedia

load_dotenv()

app = FastAPI(
    title="Multi-Source Knowledge Chatbot",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

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

    async def send_message(
        self,
        message: str,
        websocket: WebSocket,
    ):
        await websocket.send_text(message)


manager = ConnectionManager()

MAX_CHAT_HISTORY = 10

wikipedia.set_lang("en")

wikipedia.set_user_agent("WikipediaChatbot/1.0 (contact@example.com)")

wiki_api = WikipediaAPIWrapper(
    top_k_results=3,
    doc_content_chars_max=3000,
)

wiki_runner = WikipediaQueryRun(
    api_wrapper=wiki_api,
)


@tool
def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for general knowledge, historical events,
    biographies, countries, cities, science,
    technology, and encyclopedia information.
    """

    try:
        return wiki_runner.run(query)

    except Exception as e:
        return f"Wikipedia search failed: {e}"


arxiv_api = ArxivAPIWrapper(
    top_k_results=3,
    load_max_docs=3,
    doc_content_chars_max=3000,
)

arxiv_runner = ArxivQueryRun(
    api_wrapper=arxiv_api,
)


@tool
def arxiv_search(query: str) -> str:
    """
    Search academic papers from arXiv.

    Use this tool for:

    - AI
    - Machine Learning
    - Computer Science
    - Mathematics
    - Physics
    """

    try:
        return arxiv_runner.run(query)

    except Exception as e:
        return f"ArXiv search failed: {e}"


pubmed_runner = PubmedQueryRun()


@tool
def pubmed_search(query: str) -> str:
    """
    Search biomedical and medical literature from PubMed.

    Use for:

    - Diseases
    - Medicine
    - Drugs
    - Biology
    - Healthcare
    - Clinical research
    """

    try:
        return pubmed_runner.run(query)

    except Exception as e:
        return f"PubMed search failed: {e}"


duckduckgo_runner = DuckDuckGoSearchRun()


@tool
def duckduckgo_search(query: str) -> str:
    """
    Search the public web using DuckDuckGo.

    Best for:
    - recent news
    - current events
    - websites
    - programming
    - quick factual searches
    """

    try:
        return duckduckgo_runner.run(query)

    except Exception as e:
        return f"DuckDuckGo search failed: {e}"


wolfram_tool = None

if os.getenv("WOLFRAM_ALPHA_APPID"):

    wolfram_runner = WolframAlphaQueryRun(
        api_wrapper=WolframAlphaAPIWrapper()
    )

    @tool
    def wolfram_alpha(query: str) -> str:
        """
        Solve mathematical,
        scientific,
        engineering,
        unit conversion,
        geography,
        chemistry,
        and computational questions.
        """

        try:
            return wolfram_runner.run(query)

        except Exception as e:
            return f"WolframAlpha failed: {e}"

    wolfram_tool = wolfram_alpha

tavily_tool = None

if os.getenv("TAVILY_API_KEY"):

    tavily_runner = TavilySearch(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
    )

    @tool
    def tavily_search(query: str) -> str:
        """
        Search the internet using Tavily.

        Best for:

        - recent news
        - deep web research
        - long-form information
        - real-time web pages
        """

        try:
            return tavily_runner.run(query)

        except Exception as e:
            return f"Tavily search failed: {e}"

    tavily_tool = tavily_search

tools = [
    wikipedia_search,
    arxiv_search,
    pubmed_search,
    duckduckgo_search,
]

if wolfram_tool:
    tools.append(wolfram_tool)

if tavily_tool:
    tools.append(tavily_tool)


# -------------------------------------------------------
# LLM Configuration
# -------------------------------------------------------

USE_OLLAMA = True

if USE_OLLAMA:
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
        num_ctx=8192,
    )
else:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )

system_prompt = """
You are an advanced AI research assistant.

You have access to several specialized tools.

Tool Selection Rules

1. wikipedia_search
   Use for:
   - general knowledge
   - history
   - biographies
   - geography
   - famous people
   - countries
   - encyclopedia information

2. arxiv_search
   Use for:
   - Artificial Intelligence
   - Machine Learning
   - Computer Science
   - Mathematics
   - Physics
   - scientific papers

3. pubmed_search
   Use for:
   - medicine
   - diseases
   - healthcare
   - biology
   - clinical research
   - biomedical literature

4. wolfram_alpha
   Use for:
   - mathematics
   - calculations
   - equations
   - unit conversions
   - chemistry
   - physics
   - engineering

5. duckduckgo_search
   Use for:
   - recent news
   - websites
   - current events
   - programming questions
   - quick web searches

6. tavily_search
   Use for:
   - deep web research
   - comprehensive summaries
   - recent online information
   - multiple web pages

Rules

- Always choose the most appropriate tool.
- Never invent information when a tool can answer.
- If multiple tools are useful, call them sequentially.
- If no tool is required, answer directly.
- Produce clear, concise, and accurate responses.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an advanced AI research assistant with access to specialized knowledge bases and web search engines.

### Tool Selection Rules:

1. **Wikipedia (`wikipedia_search`)**:
   - Primary tool for general encyclopedia knowledge, historical events, biographies, and overview concepts.

2. **ArXiv (`arxiv_search`)**:
   - Use exclusively for academic pre-prints, computer science, physics, mathematics, and artificial intelligence research papers.

3. **PubMed (`pub_med`)**:
   - Use for biomedical, clinical, medical, healthcare, and life sciences literature.

4. **WolframAlpha (`wolfram_alpha`)**:
   - Use for exact computational data, unit conversions, geographical statistics, physical constants, and structured scientific facts.

5. **DuckDuckGo (`duckduckgo_search`)**:
   - Use for quick real-time web searches, general news, or recent developments.

6. **Tavily Search (`tavily_search_results_json`)**:
   - Use for complex web retrieval queries requiring deep content summaries from real-time web pages.

Always select the most relevant tool based on the user's domain instead of guessing.
""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

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
                    "output",
                    "Sorry, I couldn't find an answer.",
                )

                chat_history.append(HumanMessage(content=question))
                chat_history.append(AIMessage(content=answer))

                if len(chat_history) > MAX_CHAT_HISTORY:
                    chat_history = chat_history[-MAX_CHAT_HISTORY:]

                await manager.send_message(
                    f"AI: {answer}",
                    websocket,
                )

            except Exception as agent_error:
                print(f"Agent Error: {agent_error}")

                await manager.send_message(
                    "AI: Sorry, an error occurred while processing your request.",
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected.")

    except Exception as websocket_error:
        manager.disconnect(websocket)
        print(f"WebSocket Error: {websocket_error}")


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000, reload=True)
