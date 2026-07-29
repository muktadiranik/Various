import os
from typing import List
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# LangChain Imports
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_ollama.chat_models import ChatOllama

# Knowledge-Base Tool Imports
import wikipedia
from langchain_community.tools import (
    ArxivQueryRun,
    DuckDuckGoSearchRun,
    PubmedQueryRun,
    TavilySearchResults,
    WikipediaQueryRun,
)
from langchain_community.tools.wolfram_alpha import WolframAlphaQueryRun
from langchain_community.utilities import (
    ArxivAPIWrapper,
    WikipediaAPIWrapper,
    WolframAlphaAPIWrapper,
)

# Set User-Agent to comply with Wikimedia API guidelines
wikipedia.set_user_agent("WikipediaChatbot/1.0 (contact@example.com)")

load_dotenv()


# FastAPI App
app = FastAPI(title="Multi-Source Knowledge Chatbot")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# WebSocket Connection Manager
class ConnectionManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


# ------------------------------------------------------------------
# Knowledge-Base Tools Setup
# ------------------------------------------------------------------

# 1. Wikipedia Tool
wiki_api = WikipediaAPIWrapper(
    top_k_results=2,
    doc_content_chars_max=2000,
)
wiki_run = WikipediaQueryRun(api_wrapper=wiki_api)


@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for general encyclopedia knowledge, biographies, history,

    geography, and general concepts.
    """
    try:
        return wiki_run.run(query)
    except Exception as e:
        return f"Error executing Wikipedia query for '{query}': {str(e)}"


# 2. ArXiv Tool
arxiv_api = ArxivAPIWrapper(
    top_k_results=2,
    doc_content_chars_max=2000,
)
arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_api)

# 3. PubMed Tool
pubmed_tool = PubmedQueryRun()

# 4. WolframAlpha Tool
wolfram_tool = WolframAlphaQueryRun(
    api_wrapper=WolframAlphaAPIWrapper()
)

# 5. DuckDuckGo Search Tool
ddg_tool = DuckDuckGoSearchRun()

# 6. Tavily Search Tool
tavily_tool = TavilySearchResults(max_results=3)


# Register Knowledge Base Tools
tools = [
    wikipedia_search,
    arxiv_tool,
    pubmed_tool,
    wolfram_tool,
    ddg_tool,
    tavily_tool,
]


# ------------------------------------------------------------------
# LLM & Prompt Setup
# ------------------------------------------------------------------

# LLM Selection (Uncomment ChatGroq or ChatOllama based on preference)
llm = ChatOllama(model="llama3.2", temperature=0.0)

"""
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)
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


# Agent & Executor Setup
agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,  # Prevents infinite tool execution loops
    handle_parsing_errors=True,
)


# ------------------------------------------------------------------
# FastAPI Routes & WebSocket Handler
# ------------------------------------------------------------------


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"request": request}
    )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    chat_history = []

    try:
        while True:
            question = await websocket.receive_text()

            # Guarded agent execution to prevent socket disconnection on API error
            try:
                response = await agent_executor.ainvoke(
                    {
                        "question": question,
                        "chat_history": chat_history,
                    }
                )

                answer = response.get(
                    "output", "Sorry, I could not process that request."
                )

                chat_history.append(HumanMessage(content=question))
                chat_history.append(AIMessage(content=answer))

                await manager.send_message(
                    f"AI: {answer}",
                    websocket,
                )

            except Exception as agent_err:
                print(f"Agent Execution Error: {agent_err}")
                await manager.send_message(
                    "AI: Sorry, an error occurred while searching knowledge bases. Please try again.",
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket Connection Error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)