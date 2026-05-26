# app/events/publisher.py
import json
from typing import Any, Dict, Optional
from redis.asyncio import Redis
from app.core.redis_client import get_redis
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RedisEventPublisher:
    """Publish events to Redis for cross-instance communication"""

    def __init__(self):
        self.redis_client: Optional[Redis] = None

    async def _ensure_redis(self):
        """Ensure Redis connection is established"""
        if not self.redis_client:
            self.redis_client = await get_redis()

    async def publish(self, channel: str, event_type: str, data: Dict[str, Any]) -> int:
        """Publish an event to Redis channel"""
        await self._ensure_redis()

        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            subscribers = await self.redis_client.publish(channel, json.dumps(message))
            logger.debug(f"Published to {channel}: {event_type}, subscribers: {subscribers}")
            return subscribers
        except Exception as e:
            logger.error(f"Failed to publish to Redis: {e}")
            return 0

    # Message events
    async def publish_message_created(self, channel_id: int, message_data: Dict[str, Any]) -> int:
        """Publish message created event"""
        return await self.publish(
            f"channel:{channel_id}",
            "message_created",
            {
                "channel_id": channel_id,
                "message": message_data
            }
        )

    async def publish_message_updated(self, channel_id: int, message_id: int, message_data: Dict[str, Any]) -> int:
        """Publish message updated event"""
        return await self.publish(
            f"channel:{channel_id}",
            "message_updated",
            {
                "channel_id": channel_id,
                "message_id": message_id,
                "message": message_data
            }
        )

    async def publish_message_deleted(self, channel_id: int, message_id: int) -> int:
        """Publish message deleted event"""
        return await self.publish(
            f"channel:{channel_id}",
            "message_deleted",
            {
                "channel_id": channel_id,
                "message_id": message_id
            }
        )

    # Reaction events
    async def publish_reaction_added(self, channel_id: int, message_id: int, reaction_data: Dict[str, Any]) -> int:
        """Publish reaction added event"""
        return await self.publish(
            f"channel:{channel_id}",
            "reaction_added",
            {
                "channel_id": channel_id,
                "message_id": message_id,
                "reaction": reaction_data
            }
        )

    async def publish_reaction_removed(self, channel_id: int, message_id: int, reaction_data: Dict[str, Any]) -> int:
        """Publish reaction removed event"""
        return await self.publish(
            f"channel:{channel_id}",
            "reaction_removed",
            {
                "channel_id": channel_id,
                "message_id": message_id,
                "reaction": reaction_data
            }
        )

    # Presence events
    async def publish_user_presence(self, user_id: int, guild_id: int, status: str) -> int:
        """Publish user presence update event"""
        return await self.publish(
            f"guild:{guild_id}",
            "user_presence",
            {
                "user_id": user_id,
                "guild_id": guild_id,
                "status": status
            }
        )

    async def publish_typing_indicator(self, channel_id: int, user_id: int, username: str, action: str) -> int:
        """Publish typing indicator event"""
        return await self.publish(
            f"channel:{channel_id}",
            "typing_indicator",
            {
                "channel_id": channel_id,
                "user_id": user_id,
                "username": username,
                "action": action
            }
        )

    # Guild member events
    async def publish_guild_member_join(self, guild_id: int, member_data: Dict[str, Any]) -> int:
        """Publish guild member join event"""
        return await self.publish(
            f"guild:{guild_id}",
            "member_join",
            {
                "guild_id": guild_id,
                "member": member_data
            }
        )

    async def publish_guild_member_leave(self, guild_id: int, user_id: int) -> int:
        """Publish guild member leave event"""
        return await self.publish(
            f"guild:{guild_id}",
            "member_leave",
            {
                "guild_id": guild_id,
                "user_id": user_id
            }
        )

    # Channel events
    async def publish_channel_create(self, guild_id: int, channel_data: Dict[str, Any]) -> int:
        """Publish channel creation event"""
        return await self.publish(
            f"guild:{guild_id}",
            "channel_created",
            {
                "guild_id": guild_id,
                "channel": channel_data
            }
        )

    async def publish_channel_update(self, guild_id: int, channel_id: int, channel_data: Dict[str, Any]) -> int:
        """Publish channel update event"""
        return await self.publish(
            f"guild:{guild_id}",
            "channel_updated",
            {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "channel": channel_data
            }
        )

    async def publish_channel_delete(self, guild_id: int, channel_id: int) -> int:
        """Publish channel deletion event"""
        return await self.publish(
            f"guild:{guild_id}",
            "channel_deleted",
            {
                "guild_id": guild_id,
                "channel_id": channel_id
            }
        )

    # Role events
    async def publish_role_create(self, guild_id: int, role_data: Dict[str, Any]) -> int:
        """Publish role creation event"""
        return await self.publish(
            f"guild:{guild_id}",
            "role_created",
            {
                "guild_id": guild_id,
                "role": role_data
            }
        )

    async def publish_role_update(self, guild_id: int, role_id: int, role_data: Dict[str, Any]) -> int:
        """Publish role update event"""
        return await self.publish(
            f"guild:{guild_id}",
            "role_updated",
            {
                "guild_id": guild_id,
                "role_id": role_id,
                "role": role_data
            }
        )

    async def publish_role_delete(self, guild_id: int, role_id: int) -> int:
        """Publish role deletion event"""
        return await self.publish(
            f"guild:{guild_id}",
            "role_deleted",
            {
                "guild_id": guild_id,
                "role_id": role_id
            }
        )


# Global publisher instance
redis_publisher = RedisEventPublisher()