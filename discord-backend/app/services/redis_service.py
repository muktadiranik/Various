# app/services/redis_service.py
from typing import Optional, Dict, Any
from app.events.publisher import RedisEventPublisher, redis_publisher
from app.events.subscriber import RedisEventSubscriber, redis_subscriber
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """Service for Redis Pub/Sub operations"""
    
    def __init__(self):
        self.publisher: RedisEventPublisher = redis_publisher
        self.subscriber: RedisEventSubscriber = redis_subscriber
        self._initialized = False
    
    async def initialize(self):
        """Initialize Redis connections"""
        if not self._initialized:
            await self.publisher._ensure_redis()
            await self.subscriber._ensure_connection()
            self._initialized = True
            logger.info("Redis service initialized")
    
    async def start_subscriber(self):
        """Start the Redis subscriber"""
        await self.subscriber.start()
        logger.info("Redis subscriber started")
    
    async def stop_subscriber(self):
        """Stop the Redis subscriber"""
        await self.subscriber.stop()
        logger.info("Redis subscriber stopped")
    
    async def publish_message_created(self, channel_id: int, message_data: Dict[str, Any]) -> int:
        """Publish message creation event"""
        return await self.publisher.publish_message_created(channel_id, message_data)
    
    async def publish_message_updated(self, channel_id: int, message_id: int, message_data: Dict[str, Any]) -> int:
        """Publish message update event"""
        return await self.publisher.publish_message_updated(channel_id, message_id, message_data)
    
    async def publish_message_deleted(self, channel_id: int, message_id: int) -> int:
        """Publish message deletion event"""
        return await self.publisher.publish_message_deleted(channel_id, message_id)
    
    async def publish_reaction_added(self, channel_id: int, message_id: int, reaction_data: Dict[str, Any]) -> int:
        """Publish reaction added event"""
        return await self.publisher.publish_reaction_added(channel_id, message_id, reaction_data)
    
    async def publish_reaction_removed(self, channel_id: int, message_id: int, reaction_data: Dict[str, Any]) -> int:
        """Publish reaction removed event"""
        return await self.publisher.publish_reaction_removed(channel_id, message_id, reaction_data)
    
    async def publish_user_presence(self, user_id: int, guild_id: int, status: str) -> int:
        """Publish user presence update"""
        return await self.publisher.publish_user_presence(user_id, guild_id, status)
    
    async def publish_typing_indicator(self, channel_id: int, user_id: int, username: str, action: str) -> int:
        """Publish typing indicator"""
        return await self.publisher.publish_typing_indicator(channel_id, user_id, username, action)
    
    async def publish_guild_member_join(self, guild_id: int, member_data: Dict[str, Any]) -> int:
        """Publish guild member join event"""
        return await self.publisher.publish_guild_member_join(guild_id, member_data)
    
    async def publish_guild_member_leave(self, guild_id: int, user_id: int) -> int:
        """Publish guild member leave event"""
        return await self.publisher.publish_guild_member_leave(guild_id, user_id)
    
    async def publish_channel_create(self, guild_id: int, channel_data: Dict[str, Any]) -> int:
        """Publish channel creation event"""
        return await self.publisher.publish_channel_create(guild_id, channel_data)
    
    async def publish_channel_update(self, guild_id: int, channel_id: int, channel_data: Dict[str, Any]) -> int:
        """Publish channel update event"""
        return await self.publisher.publish_channel_update(guild_id, channel_id, channel_data)
    
    async def publish_channel_delete(self, guild_id: int, channel_id: int) -> int:
        """Publish channel deletion event"""
        return await self.publisher.publish_channel_delete(guild_id, channel_id)
    
    async def publish_role_create(self, guild_id: int, role_data: Dict[str, Any]) -> int:
        """Publish role creation event"""
        return await self.publisher.publish_role_create(guild_id, role_data)
    
    async def publish_role_update(self, guild_id: int, role_id: int, role_data: Dict[str, Any]) -> int:
        """Publish role update event"""
        return await self.publisher.publish_role_update(guild_id, role_id, role_data)
    
    async def publish_role_delete(self, guild_id: int, role_id: int) -> int:
        """Publish role deletion event"""
        return await self.publisher.publish_role_delete(guild_id, role_id)
    
    async def subscribe_to_guild(self, guild_id: int):
        """Subscribe to guild events"""
        await self.subscriber.subscribe_to_guild(guild_id)
    
    async def subscribe_to_channel(self, channel_id: int):
        """Subscribe to channel events"""
        await self.subscriber.subscribe_to_channel(channel_id)
    
    async def subscribe_to_user(self, user_id: int):
        """Subscribe to user events"""
        await self.subscriber.subscribe_to_user(user_id)
    
    async def unsubscribe(self, channels: list):
        """Unsubscribe from channels"""
        await self.subscriber.unsubscribe(channels)


# Global instance
redis_service = RedisService()