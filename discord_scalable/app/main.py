from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db, close_db, close_redis
from app.routers import messages  # Sample
from app.websocket.manager import router as ws_router
# Import models to create tables

from app.models import *  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()
    await close_redis()

app = FastAPI(
    title="Discord Scalable API",
    description="Scalable Discord-like backend with async FastAPI, WS, Redis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages.router, prefix="/api/v1", tags=["messages"])
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"message": "Discord Scalable API running - check /docs"}
