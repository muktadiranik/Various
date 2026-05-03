from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
import json
from app.database import get_async_db, get_redis
from app.models.user import User
from app.models.room import Room
from app.database import AsyncSessionLocal

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int, redis, db):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][str(user_id)] = websocket

        # Online tracking with Redis TTL
        await redis.setex(f"online:{room_id}:{user_id}", 30, "1")
        await redis.sadd(f"online_room:{room_id}", user_id)

        # Broadcast join
        await self.broadcast(room_id, {"type": "user_joined", "user_id": user_id, "online_count": await redis.scard(f"online_room:{room_id}")})

    def disconnect(self, websocket: WebSocket, room_id: int, user_id: int, redis):
        if room_id in self.active_connections:
            self.active_connections[room_id].pop(str(user_id), None)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

        # Remove online
        redis.srem(f"online_room:{room_id}", user_id)
        # Broadcast leave
        # Note: async needed, but since sync def, call async

    async def send_personal(self, message: dict, room_id: int, to_user_id: int):
        if room_id in self.active_connections and str(to_user_id) in self.active_connections[room_id]:
            await self.active_connections[room_id][str(to_user_id)].send_json(message)

    async def broadcast(self, room_id: int, message: dict):
        if room_id in self.active_connections:
            for connection in list(self.active_connections[room_id].values()):
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


async def get_user_and_room(room_id: int, token: str, db: AsyncSession) -> tuple[User, Room]:
    result = await db.execute(select(User).where(User.username == token))
    user = result.scalar_one_or_none()
    if not user:
        user = User(username=token)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "Room not found")
    return user, room


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_async_db)
):
    redis = await get_redis()
    user, room = await get_user_and_room(room_id, token, db)
    await manager.connect(websocket, room_id, user.id, redis, db)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "heartbeat":
                await redis.expire(f"online:{room_id}:{user.id}", 30)
                continue

            if msg_type in ["typing_start", "typing_stop"]:
                await manager.broadcast(room_id, {"type": msg_type, "user_id": user.id, "username": user.username})
                continue

            if msg_type == "message":
                # Optional persist
                await manager.broadcast(room_id, {
                    "type": "message",
                    "content": data.get("content"),
                    "user_id": user.id,
                    "username": user.username,
                    "timestamp": "now"
                })
                continue

            # Default broadcast
            await manager.broadcast(room_id, data)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, user.id, redis)
        await manager.broadcast(room_id, {"type": "user_left", "user_id": user.id})
