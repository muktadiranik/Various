from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.message import Message
from app.schemas.message import MessageCreate


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, message_create: MessageCreate, user_id: int) -> Message:
        db_message = Message(**message_create.model_dump(), user_id=user_id)
        self.db.add(db_message)
        await self.db.commit()
        await self.db.refresh(db_message)
        return db_message

    async def get_by_channel(self, channel_id: int, limit: int = 50) -> List[Message]:
        result = await self.db.execute(
            select(Message).where(Message.channel_id == channel_id).order_by(
                Message.timestamp.desc()).limit(limit)
        )
        return result.scalars().all()
