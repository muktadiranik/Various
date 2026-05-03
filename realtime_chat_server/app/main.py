from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db, close_db, close_redis
from app.websocket.manager import router as text_router
from app.websocket.voice import router as voice_router
from app.websocket.video import router as video_router
from app.routers.rooms import router as rooms_router
from app.routers.messages import router as messages_router
from app.routers.users import router as users_router
# Import models to create tables
from app.models import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()
    await close_redis()

app = FastAPI(
    title="Real-Time Chat Server",
    description="FastAPI realtime chat with rooms, typing, online users, Redis/SQLite",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms_router, prefix="/api", tags=["rooms"])
app.include_router(messages_router, prefix="/api", tags=["messages"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(text_router)
app.include_router(voice_router)
app.include_router(video_router)


@app.get("/")
async def root():
    return {"message": "Real-Time Chat Server - /docs for API, WS /ws/{room_id}?token={username}"}
