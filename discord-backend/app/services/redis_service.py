# app/services/redis_service.py
from typing import Optional, Dict, Any
from app.events.publisher import RedisEventPublisher, redis_publisher
from app.events.subscriber import RedisEventSubscriber, redis_subscriber
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.publisher: RedisEventPublisher = redis_publisher
        self.subscriber: RedisEventSubscriber = redis_subscriber
        self._initialized = False
    
    async def initialize(self):
        if not self._initialized:
            await self.publisher._ensure_redis()
            await self.subscriber._ensure_connection()
            self._initialized = True
            logger.info("Redis service initialized")
    
    async def start_subscriber(self):
        await self.subscriber.start()
    
    async def stop_subscriber(self):
        await self.subscriber.stop()
    
    async def publish_message_created(self, channel_id: int, message_data: Dict[str, Any]) -> int:
        return await self.publisher.publish_message_created(channel_id, message_data)
    
    async def publish_message_updated(self, channel_id: int, message_id: int, message_data: Dict[str, Any]) -> int:
        return await self.publisher.publish_message_updated(channel_id, message_id, message_data)
    
    async def publish_message_deleted(self, channel_id: int, message_id: int) -> int:
        return await self.publisher.publish_message_deleted(channel_id, message_id)
    
    async def publish_user_presence(self, user_id: int, guild_id: int, status: str) -> int:
        return await self.publisher.publish_user_presence(user_id, guild_id, status)
    
    async def publish_typing_indicator(self, channel_id: int, user_id: int, username: str, action: str) -> int:
        return await self.publisher.publish_typing_indicator(channel_id, user_id, username, action)

redis_service = RedisService()