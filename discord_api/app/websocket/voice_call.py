from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict
from ..database import get_db
from ..models.user import User
from ..models.server import ServerMember
from ..models.channel import Channel, ChannelType
from ..routers.auth import oauth2_scheme
from ..core.security import get_current_user
from ..routers.auth import oauth2_scheme
from ..database import get_db
from datetime import datetime

router = APIRouter()


class VoiceManager:
    def __init__(self):
        # channel_id -> user_id -> ws
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel_id: int, user_id: int):
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = {}
        self.active_connections[channel_id][str(user_id)] = websocket
        await self.broadcast(channel_id, {'type': 'user_joined', 'user_id': user_id, 'timestamp': datetime.now().isoformat()})

    def disconnect(self, websocket: WebSocket, channel_id: int, user_id: int):
        if channel_id in self.active_connections:
            self.active_connections[channel_id].pop(str(user_id), None)
            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]

    async def send_personal(self, message: dict, channel_id: int, to_user_id: int, from_user_id: int):
        if channel_id in self.active_connections:
            to_ws = self.active_connections[channel_id].get(str(to_user_id))
            if to_ws:
                message['from'] = from_user_id
                await to_ws.send_json(message)

    async def broadcast(self, channel_id: int, message: dict):
        if channel_id in self.active_connections:
            for ws in self.active_connections[channel_id].values():
                await ws.send_json(message)


manager_voice = VoiceManager()


@router.websocket("/ws/voice/{channel_id}")
async def websocket_voice_endpoint(
    websocket: WebSocket,
    channel_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    # Same auth as text
    current_user = get_current_user(token)
    if not current_user:
        await websocket.close(code=1008)
        return
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        await websocket.close(code=1008)
        return
    channel = db.query(Channel).filter(
        Channel.id == channel_id, Channel.type == ChannelType.VOICE).first()
    if not channel:
        await websocket.close(code=1008)
        return
    member = db.query(ServerMember).filter(ServerMember.server_id ==
                                           channel.server_id, ServerMember.user_id == user.id).first()
    if not member:
        await websocket.close(code=1008)
        return

    await manager_voice.connect(websocket, channel_id, user.id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get('type')
            if msg_type == 'offer':
                await manager_voice.send_personal(data, channel_id, data.get('to_user_id'), user.id)
            elif msg_type == 'answer':
                await manager_voice.send_personal(data, channel_id, data.get('to_user_id'), user.id)
            elif msg_type == 'ice-candidate':
                await manager_voice.send_personal(data, channel_id, data.get('to_user_id'), user.id)
            else:
                await manager_voice.broadcast(channel_id, {'type': msg_type, 'user_id': user.id, 'data': data})
    except WebSocketDisconnect:
        manager_voice.disconnect(websocket, channel_id, user.id)
