from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
from app.database import get_async_db
from app.schemas.message import MessageCreate, MessageOut
from app.services.message import MessageService
from app.websocket.manager import manager
from app.database import get_async_db

router = APIRouter()


@router.post("/messages/", response_model=MessageOut)
async def send_message(
    message: MessageCreate,
    user_id: int = 1,
    db: AsyncSession = Depends(get_async_db)
):
    db_message = await MessageService.create_message(message, user_id)
    broadcast_msg = {
        "type": "message",
        "content": message.content,
        "user_id": user_id,
        "message_id": db_message.id,
        "timestamp": db_message.timestamp.isoformat()
    }
    await manager.broadcast(message.channel_id, broadcast_msg)
    return db_message


@router.get("/messages/channel/{channel_id}", response_model=List[MessageOut])
async def get_messages(channel_id: int, db: AsyncSession = Depends(get_async_db)):
    return await MessageService.get_recent_messages(channel_id)
