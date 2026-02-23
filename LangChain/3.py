import os
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from typing import List

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.messages import AIMessage, HumanMessage
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool

from dotenv import load_dotenv
load_dotenv()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def dicsonnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def chat(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()

app = FastAPI(title="RAG Agent")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@tool
def divide(a: int, b: int) -> int:
    """Divide two numbers."""
    return a / b


tools = [add, subtract, multiply, divide]

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant with tools."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(
    tools=tools,
    llm=model,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    chat_history = []

    try:
        while True:
            user_input = await websocket.receive_text()

            response = await agent_executor.ainvoke(
                {
                    "question": user_input,
                    "chat_history": chat_history
                }
            )

            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=response["output"]))

            await manager.chat(f"AI: {response['output']}", websocket)
    except WebSocketDisconnect:
        manager.dicsonnect(websocket)

    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()


@app.get("/")
async def root():
    return {"message": "LangChain Agent Bot is running. Connect via /ws/chat"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
