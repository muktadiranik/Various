import asyncio
import json
import uuid
from typing import Dict, Set, Optional
from aioredis import Redis
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from .schemas import WSMessage, MessageType, TypingEvent


class RTCConnectionManager:
    def __init__(self, redis: Redis):
        self.redis = redis
        # room_id -> set(client_ids)
        self.active_rooms: Dict[str, Set[str]] = {}
        self.client_rooms: Dict[str, str] = {}  # client_id -> room_id

    async def connect(self, websocket: WebSocket, room_id: str, client_id: str):
        await websocket.accept()
        self.active_rooms.setdefault(room_id, set()).add(client_id)
        self.client_rooms[client_id] = room_id

        # Publish presence update
        await self.redis.publish(f"room:{room_id}:presence", json.dumps({
            "type": "presence_update",
            "online_users": len(self.active_rooms[room_id]),
            "user_joined": client_id
        }))

        # Subscribe to room channels
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"room:{room_id}:msg", f"room:{room_id}:presence", f"room:{room_id}:typing")

        # Background task to forward pubsub messages
        async def forward_messages():
            async for message in pubsub.listen():
                if message["type"] == "message" and websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(message["data"])

        task = asyncio.create_task(forward_messages())

        try:
            while True:
                data = await websocket.receive_text()
                msg = WSMessage.model_validate_json(data)
                await self._handle_message(websocket, room_id, client_id, msg)
        except WebSocketDisconnect:
            task.cancel()
            await self.disconnect(room_id, client_id)
            await pubsub.close()

    async def disconnect(self, room_id: str, client_id: str):
        if room_id in self.active_rooms:
            self.active_rooms[room_id].discard(client_id)
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]
        self.client_rooms.pop(client_id, None)

        # Clear typing if any
        await self.redis.hdel(f"room:{room_id}:typing", client_id)

        # Publish presence update
        await self.redis.publish(f"room:{room_id}:presence", json.dumps({
            "type": "presence_update",
            "online_users": len(self.active_rooms.get(room_id, set())),
            "user_left": client_id
        }))

    async def _handle_message(self, websocket: WebSocket, room_id: str, client_id: str, msg: WSMessage):
        if msg.type == MessageType.JOIN:
            # Already joined on connect
            pass
        elif msg.type in (MessageType.TYPING_START, MessageType.TYPING_STOP):
            typing = msg.type == MessageType.TYPING_START
            if typing:
                await self.redis.hset(f"room:{room_id}:typing", client_id, "1")
                # TTL 3s per user? Wait, per typing session
                await self.redis.expire(f"room:{room_id}:typing", 3)
            else:
                await self.redis.hdel(f"room:{room_id}:typing", client_id)

            # Broadcast typing list
            typing_users = await self.redis.hkeys(f"room:{room_id}:typing")
            await self.redis.publish(f"room:{room_id}:typing", json.dumps({
                "type": "typing_update",
                "typing_users": list(typing_users)
            }))
        else:
            # Broadcast message (text, sdp, ice)
            broadcast_data = {
                "type": msg.type,
                "content": msg.content,
                "data": msg.data,
                "from": client_id
            }
            await self.redis.publish(f"room:{room_id}:msg", json.dumps(broadcast_data))

    async def get_online_users(self, room_id: str) -> list:
        # Could fetch from Redis set, but for simplicity use active_rooms
        return list(self.active_rooms.get(room_id, set()))
