import os
import uvicorn
from typing import List
from dotenv import load_dotenv
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
load_dotenv()


# FastAPI
app = FastAPI(title="Wikipedia Chatbot")

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


# Calculator Tools
@tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@tool
def divide(a: float, b: float):
    """Divide two numbers."""
    if b == 0:
        return "Cannot divide by zero."
    return a / b


# Wikipedia Tool
wiki_api = WikipediaAPIWrapper(
    top_k_results=2,
    doc_content_chars_max=2000,
)

wiki = WikipediaQueryRun(api_wrapper=wiki_api)


@tool
def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for factual information about
    people, places, science, history, technology,
    organizations, books, movies, etc.
    """
    return wiki.run(query)


# Register Tools
tools = [
    add,
    subtract,
    multiply,
    divide,
    wikipedia_search,
]


# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)


# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    You are a helpful AI assistant.

    You have access to several tools.

    Use the Wikipedia tool whenever the user asks about:

    - people
    - countries
    - cities
    - history
    - science
    - technology
    - medicine
    - programming
    - organizations
    - books
    - movies
    - animals
    - geography

    Use the calculator tools for mathematical operations.

    Always use the appropriate tool instead of guessing.
    """,
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


# Agent
agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)


# Routes
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


# WebSocket Chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):

    await manager.connect(websocket)

    chat_history = []

    try:
        while True:

            question = await websocket.receive_text()

            response = await agent_executor.ainvoke(
                {
                    "question": question,
                    "chat_history": chat_history,
                }
            )

            answer = response["output"]

            chat_history.append(HumanMessage(content=question))
            chat_history.append(AIMessage(content=answer))

            await manager.send_message(
                f"AI: {answer}",
                websocket,
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception as e:
        print(e)
        manager.disconnect(websocket)
