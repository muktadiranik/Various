from app.websocket.video_call import video_router
from app.websocket.voice_call import router as voice_router
from app.websocket.text_chat import router as text_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, users, servers, channels
# from app.websocket import text_chat, voice_call, video_call

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Discord-like API",
    description="FastAPI Discord clone with WebSockets for text/voice/video",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users, prefix="/api/v1/users", tags=["users"])
app.include_router(servers, prefix="/api/v1/servers", tags=["servers"])
app.include_router(channels, prefix="/api/v1/channels", tags=["channels"])

app.include_router(text_router)
app.include_router(voice_router)
app.include_router(video_router)

# WebSocket endpoints included
# For now, placeholder


@app.get("/")
def read_root():
    return {"message": "Discord API - /docs"}
