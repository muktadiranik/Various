from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_async_db
from app.models.message import Message
from app.models.room import Room
from app.schemas.message import MessageList, MessageOut, MessageCreate


router = APIRouter()


@router.get("/rooms/{room_id}/messages", response_model=MessageList)
async def get_messages(room_id: int, limit: int = 50, db: AsyncSession = Depends(get_async_db)):
    result_room = await db.execute(select(Room).where(Room.id == room_id))
    if not result_room.scalar_one_or_none():
        raise HTTPException(404, "Room not found")

    result = await db.execute(
        select(Message).where(Message.room_id == room_id)
        .order_by(Message.timestamp.desc()).limit(limit)
    )
    messages = result.scalars().all()
    return {"messages": messages[::-1]}  # Newest first reverse


@router.post("/rooms/{room_id}/messages", response_model=MessageOut)
async def create_message(room_id: int, message_in: MessageCreate, db: AsyncSession = Depends(get_async_db)):
    result_room = await db.execute(select(Room).where(Room.id == room_id))
    room = result_room.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "Room not found")

    db_message = Message(**message_in.model_dump())
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message
