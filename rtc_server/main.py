from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from aioredis import Redis, from_url
import uuid
import uvicorn
import os

from .models import Base, User, Room, RoomMember, Message
from .schemas import UserCreate, UserOut, RoomCreate, RoomOut, MessageOut, WebRTCSignaling
from .connection_manager import RTCConnectionManager

DATABASE_URL = "sqlite+aiosqlite:///./rtc.db"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False)

redis_client: Redis = None
manager: RTCConnectionManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client, manager
    redis_client = await from_url(REDIS_URL)
    manager = RTCConnectionManager(redis_client)

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown
    await redis_client.close()
    await async_engine.dispose()

app = FastAPI(title="RTC Server",
              description="Real-Time Communication Server with WebRTC Signaling", lifespan=lifespan)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Users


@app.post("/users/", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(username=user.username)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Rooms


@app.post("/rooms/", response_model=RoomOut)
async def create_room(room: RoomCreate, owner_id: int, db: AsyncSession = Depends(get_db)):
    db_room = Room(name=room.name, owner_id=owner_id)
    db.add(db_room)
    await db.commit()
    await db.refresh(db_room)
    return db_room


@app.get("/rooms/{room_id}", response_model=RoomOut)
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

# Join room (for persistence)


@app.post("/rooms/{room_id}/join")
async def join_room(room_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    member = RoomMember(user_id=user_id, room_id=room_id)
    db.add(member)
    await db.commit()
    return {"status": "joined"}

# WebSocket


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, room_id, client_id)

if __name__ == "__main__":
    print("To run the server:")
    print("uvicorn rtc_server.main:app --reload")
    print("Make sure you are in d:/Data/Python/Various")
    print("Also start Redis: redis-server")
