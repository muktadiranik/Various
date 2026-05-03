from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.server import ServerMember
from ..models.channel import Channel, ChannelType
from ..routers.auth import oauth2_scheme
from ..core.security import get_current_user
from datetime import datetime

# Reuse VoiceManager logic, same for video
from .voice_call import VoiceManager, router as voice_router
manager_video = VoiceManager()

video_router = APIRouter()


@video_router.websocket("/ws/video/{channel_id}")
async def websocket_video_endpoint(websocket: WebSocket, channel_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    # Identical to voice, but video channel
    current_user = get_current_user(token)
    if not current_user:
        await websocket.close(code=1008)
        return
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        await websocket.close(code=1008)
        return
    channel = db.query(Channel).filter(Channel.id == channel_id, Channel.type ==
                                       ChannelType.VOICE).first()  # voice channels for video too or add VIDEO type
    if not channel:
        await websocket.close(code=1008)
        return
    member = db.query(ServerMember).filter(ServerMember.server_id ==
                                           channel.server_id, ServerMember.user_id == user.id).first()
    if not member:
        await websocket.close(code=1008)
        return

    await manager_video.connect(websocket, channel_id, user.id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get('type')
            if msg_type in ['offer', 'answer', 'ice-candidate']:
                await manager_video.send_personal(data, channel_id, data.get('to_user_id'), user.id)
            else:
                await manager_video.broadcast(channel_id, {'type': msg_type, 'user_id': user.id, 'data': data})
    except WebSocketDisconnect:
        manager_video.disconnect(websocket, channel_id, user.id)
