from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db, get_redis
from app.models.user import User
from app.models.room import RoomType
from .manager import ConnectionManager, get_user_and_room

router = APIRouter()


manager_video = ConnectionManager()


@router.websocket("/ws/video/{room_id}")
async def websocket_video_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_async_db),
):
    user, room = await get_user_and_room(room_id, token, db)
    if room.type != RoomType.VIDEO:
        raise HTTPException(400, "Not a video room")
    redis = await get_redis()
    await manager_video.connect(websocket, room_id, user.id, redis, db)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type in ["offer", "answer", "ice-candidate"]:
                to_user_id = data.get("to_user_id")
                await manager_video.send_personal(data, room_id, to_user_id)
            else:
                await manager_video.broadcast(room_id, data)
    except WebSocketDisconnect:
        manager_video.disconnect(websocket, room_id, user.id, redis)
        await manager_video.broadcast(room_id, {"type": "user_left_video", "user_id": user.id})
