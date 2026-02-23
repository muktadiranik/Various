from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_ollama.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from dotenv import load_dotenv
load_dotenv()

# Langchain imports


loader = WebBaseLoader("https://www.thedailystar.net/")
documents = loader.load()

splitters = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = splitters.split_documents(documents)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(splits, embeddings)
retriever = vectorstore.as_retriever()


def format_documents(documents) -> str:
    return "\n\n".join([document.page_content for document in documents])


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant that answers questions based on the provided {context}."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])


rag_chain = (
    {
        "context": lambda x: format_documents(retriever.invoke(x["question"])),
        "chat_history": lambda x: x["chat_history"],
        "question": lambda x: x["question"],
    }
    | prompt
    | model
    | StrOutputParser()
)

chat_history = []


# --- 3. FASTAPI SERVER ---
app = FastAPI(title="RAG Chatbot")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def chat(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    # Serve HTML file for the chat interface
    return templates.TemplateResponse(
        name="index.html",
        context={"request": request}
    )


@app.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    # 1. Create a history list specifically for THIS user connection
    # If you put this outside the function, everyone shares the same memory!
    local_chat_history = []

    try:
        while True:
            # Receive message from the browser/client
            user_input = await websocket.receive_text()

            # 2. FIX: Pass a dictionary containing BOTH required keys
            # We use 'await' with 'ainvoke' for better performance in FastAPI
            response = await rag_chain.ainvoke({
                "question": user_input,
                "chat_history": local_chat_history
            })

            # 3. FIX: Save the exchange to history so the AI remembers it next time
            local_chat_history.append(HumanMessage(content=user_input))
            local_chat_history.append(AIMessage(content=response))

            # Send the response back to the user
            await manager.chat(f"AI: {response}", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()


@app.get("/")
async def root():
    return {"message": "LangChain RAG Bot is running. Connect via /ws/chat"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
