import uvicorn
import os
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from typing import List

# Langchain imports
from langchain_community.document_loaders import RecursiveUrlLoader
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

# Hugging Face imports
from huggingface_hub import login

# Import the dotenv library
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Login to the Hugging Face API
login(token=os.getenv("HF_TOKEN"))


# --- 1. LIST OF SOURCE URLS ---
# Each URL here will be crawled, along with its sub-pages, up to MAX_DEPTH links deep.
URLS = [
    "https://www.thedailystar.net/",
    "https://www.prothomalo.com/",
    "https://www.bbc.com/news",
]

# How many link-hops deep to crawl from each starting URL.
# 1 = only the page itself, 2 = the page + pages it links to, etc.
# Go carefully with this - depth 3+ on a large site can mean thousands of pages.
MAX_DEPTH = 3

# Cap on total pages pulled per starting URL, so one huge site can't blow up
# the crawl or your machine's memory.
MAX_PAGES_PER_SITE = 200


def extractor(html: str) -> str:
    """Strip HTML down to visible text for cleaner chunks/embeddings."""
    return BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)


def load_all_documents(urls: List[str]):
    """Recursively crawl each starting URL (and its sub-URLs) individually so
    one bad or slow site doesn't kill the whole batch."""
    all_documents = []
    for url in urls:
        try:
            print(f"Crawling: {url} (max_depth={MAX_DEPTH})")
            loader = RecursiveUrlLoader(
                url=url,
                max_depth=MAX_DEPTH,
                extractor=extractor,
                # Stay on the same domain as the starting URL - don't follow
                # external links off-site.
                prevent_outside=True,
                # Basic UA header helps avoid being blocked by some sites.
                headers={"User-Agent": "Mozilla/5.0 (compatible; RAGBot/1.0)"},
                timeout=10,
            )
            docs = loader.load()[:MAX_PAGES_PER_SITE]
            for doc in docs:
                doc.metadata["source_url"] = doc.metadata.get("source", url)
            all_documents.extend(docs)
            print(
                f"  -> Loaded {len(docs)} page(s) from {url} and its sub-URLs")
        except Exception as e:
            print(f"  -> Failed to crawl {url}: {e}")
    return all_documents


# Load the documents
documents = load_all_documents(URLS)

# Split the documents into chunks
splitters = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = splitters.split_documents(documents)

# Create the embeddings
embeddings = HuggingFaceEmbeddings(model_name=os.getenv("HF_MODEL_NAME"))

# Create the vector store
vectorstore = Chroma.from_documents(splits, embeddings)

# Create the retriever
retriever = vectorstore.as_retriever()


def format_documents(documents) -> str:
    # Include the source URL alongside each chunk so the model (and you,
    # when debugging) can see which site a piece of context came from.
    return "\n\n".join([
        f"[Source: {document.metadata.get('source_url', 'unknown')}]\n{document.page_content}"
        for document in documents
    ])


model = ChatOllama(model="llama3.2", temperature=0.0)

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


# --- 2. FASTAPI SERVER ---
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
        request=request,
        name="index.html",
        context={"request": request}
    )


@app.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    # Per-connection chat history so users don't share memory
    local_chat_history = []

    try:
        while True:
            user_input = await websocket.receive_text()

            response = await rag_chain.ainvoke({
                "question": user_input,
                "chat_history": local_chat_history
            })

            local_chat_history.append(HumanMessage(content=user_input))
            local_chat_history.append(AIMessage(content=response))

            await manager.chat(f"AI: {response}", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()
