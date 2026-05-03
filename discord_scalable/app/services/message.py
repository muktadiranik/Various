from app.repositories.message import MessageRepository
from app.schemas.message import MessageCreate, MessageOut
from app.database import get_async_db
from app.core.cache import cache
from app.database import get_redis
import json


class MessageService:
    @staticmethod
    @cache(ttl=60)  # Cache recent messages per channel
    async def get_recent_messages(channel_id: int, limit: int = 50) -> list[MessageOut]:
        db = await get_async_db().__anext__()
        repo = MessageRepository(db)
        messages = await repo.get_by_channel(channel_id, limit)
        return [MessageOut.model_validate(m) for m in messages]

    @staticmethod
    async def create_message(message_create: MessageCreate, user_id: int) -> MessageOut:
        db = await get_async_db().__anext__()
        repo = MessageRepository(db)
        db_message = await repo.create(message_create, user_id)
        # Invalidate cache
        redis = await get_redis()
        await redis.delete(f"cache:get_recent_messages:{hash(str([message_create.channel_id]))}")
        return MessageOut.model_validate(db_message)
