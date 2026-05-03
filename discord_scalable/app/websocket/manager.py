from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict
import json
from app.database import get_async_db
from app.models.server import ServerMember
from app.models.channel import Channel

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel_id: int, user_id: int):
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = {}
        self.active_connections[channel_id][str(user_id)] = websocket
        await self.broadcast(channel_id, {"type": "user_joined", "user_id": user_id})

    def disconnect(self, websocket: WebSocket, channel_id: int, user_id: int):
        if channel_id in self.active_connections:
            self.active_connections[channel_id].pop(str(user_id), None)
            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]

    async def send_personal(self, message: dict, channel_id: int, to_user_id: int):
        if channel_id in self.active_connections and str(to_user_id) in self.active_connections[channel_id]:
            await self.active_connections[channel_id][str(to_user_id)].send_json(message)

    async def broadcast(self, channel_id: int, message: dict | str):
        if channel_id in self.active_connections:
            msg = message if isinstance(message, dict) else json.loads(message)
            for connection in self.active_connections[channel_id].values():
                try:
                    await connection.send_json(msg)
                except:
                    pass


manager = ConnectionManager()


async def get_valid_channel(channel_id: int, user_id: int, db: AsyncSession) -> Channel:
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(404, "Channel not found")
    result = await db.execute(
        select(ServerMember).where(
            ServerMember.server_id == channel.server_id,
            ServerMember.user_id == user_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(403, "Not a server member")
    return channel


@router.websocket("/ws/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_async_db)
):
    user_id = int(token)
    channel = await get_valid_channel(channel_id, user_id, db)
    await manager.connect(websocket, channel_id, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get('type')
            if msg_type in ['offer', 'answer', 'ice-candidate']:
                to_user_id = data.get('to_user_id')
                await manager.send_personal(data, channel_id, to_user_id)
            else:
                await manager.broadcast(channel_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id, user_id)
