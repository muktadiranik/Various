from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Set
from ..database import get_db
from ..models.user import User
from ..models.server import ServerMember
from ..models.channel import Channel
from ..routers.auth import oauth2_scheme
from ..core.security import get_current_user
from ..routers.servers import get_current_user_obj

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        # channel_id -> user_id -> ws
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel_id: int, user_id: int):
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = {}
        self.active_connections[channel_id][str(user_id)] = websocket
        # Notify others
        await self.broadcast(channel_id, f"User {user_id} joined text chat")

    def disconnect(self, websocket: WebSocket, channel_id: int, user_id: int):
        if channel_id in self.active_connections:
            self.active_connections[channel_id].pop(str(user_id), None)
            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]

    async def send_personal(self, message: dict, channel_id: int, user_id: int):
        if channel_id in self.active_connections and str(user_id) in self.active_connections[channel_id]:
            await self.active_connections[channel_id][str(user_id)].send_json(message)

    async def broadcast(self, message: str, channel_id: int):
        if channel_id in self.active_connections:
            for connection in self.active_connections[channel_id].values():
                await connection.send_text(message)


manager_text = ConnectionManager()


async def get_valid_channel(channel_id: int, current_user=Depends(get_current_user_obj), db: Session = Depends(get_db)):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404)
    member = db.query(ServerMember).filter(ServerMember.server_id ==
                                           channel.server_id, ServerMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=403)
    return channel


@router.websocket("/ws/text/{channel_id}")
async def websocket_text_endpoint(
    websocket: WebSocket,
    channel_id: int,
    token: str = Query(...),
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Validate token/user (simple)
    if not current_user:
        await websocket.close(code=1008)
        return
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        await websocket.close(code=1008)
        return
    channel = db.query(Channel).filter(
        Channel.id == channel_id, Channel.type == 'text').first()
    if not channel:
        await websocket.close(code=1008)
        return
    member = db.query(ServerMember).filter(ServerMember.server_id ==
                                           channel.server_id, ServerMember.user_id == user.id).first()
    if not member:
        await websocket.close(code=1008)
        return

    await manager_text.connect(websocket, channel_id, user.id)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast message
            message = {
                'type': 'message',
                'content': data.get('content'),
                'user_id': user.id,
                'username': user.username,
                'timestamp': 'now'
            }
            await manager_text.broadcast(str(message), channel_id)
    except WebSocketDisconnect:
        manager_text.disconnect(websocket, channel_id, user.id)
