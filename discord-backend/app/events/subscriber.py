# app/events/subscriber.py
import json
import asyncio
from typing import Dict, Any, Optional, Set
from datetime import datetime
from redis.asyncio import Redis
from app.core.redis_client import get_redis
from app.core.websocket_manager import websocket_manager
from app.services.presence_service import presence_service
import logging

logger = logging.getLogger(__name__)


class RedisEventSubscriber:
    """Subscribe to Redis events and broadcast to WebSocket clients"""

    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self.pubsub = None
        self.subscribed_channels: Set[str] = set()
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def _ensure_connection(self):
        """Ensure Redis connection is established"""
        if not self.redis_client:
            self.redis_client = await get_redis()
            self.pubsub = self.redis_client.pubsub()

    async def subscribe(self, channels: list):
        """Subscribe to Redis channels"""
        await self._ensure_connection()

        for channel in channels:
            if channel not in self.subscribed_channels:
                await self.pubsub.subscribe(channel)
                self.subscribed_channels.add(channel)
                logger.info(f"Subscribed to Redis channel: {channel}")

    async def unsubscribe(self, channels: list):
        """Unsubscribe from Redis channels"""
        if not self.pubsub:
            return

        for channel in channels:
            if channel in self.subscribed_channels:
                await self.pubsub.unsubscribe(channel)
                self.subscribed_channels.discard(channel)
                logger.info(f"Unsubscribed from Redis channel: {channel}")

    async def subscribe_to_guild(self, guild_id: int):
        """Subscribe to all channels related to a guild"""
        channels = [
            f"guild:{guild_id}",
            f"guild:{guild_id}:members",
            f"guild:{guild_id}:channels"
        ]
        await self.subscribe(channels)

    async def subscribe_to_channel(self, channel_id: int):
        """Subscribe to a specific channel's events"""
        channels = [
            f"channel:{channel_id}",
            f"channel:{channel_id}:messages",
            f"channel:{channel_id}:reactions"
        ]
        await self.subscribe(channels)

    async def subscribe_to_user(self, user_id: int):
        """Subscribe to user-specific events"""
        channels = [
            f"user:{user_id}",
            f"user:{user_id}:notifications"
        ]
        await self.subscribe(channels)

    async def _handle_message(self, channel: str, message_data: Dict[str, Any]):
        """Handle incoming Redis message and broadcast to WebSocket clients"""
        event_type = message_data.get("type")
        data = message_data.get("data", {})
        timestamp = message_data.get("timestamp", datetime.utcnow().isoformat())

        try:
            # Message events
            if event_type == "message_created":
                channel_id = data.get("channel_id")
                message = data.get("message")

                if channel_id and message:
                    await websocket_manager.broadcast_to_channel(
                        channel_id,
                        {
                            "type": "new_message",
                            "data": message,
                            "channel_id": channel_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted message_created to channel {channel_id}")

            elif event_type == "message_updated":
                channel_id = data.get("channel_id")
                message_id = data.get("message_id")
                message = data.get("message")

                if channel_id and message_id:
                    await websocket_manager.broadcast_to_channel(
                        channel_id,
                        {
                            "type": "message_updated",
                            "message_id": message_id,
                            "data": message,
                            "channel_id": channel_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted message_updated to channel {channel_id}")

            elif event_type == "message_deleted":
                channel_id = data.get("channel_id")
                message_id = data.get("message_id")

                if channel_id and message_id:
                    await websocket_manager.broadcast_to_channel(
                        channel_id,
                        {
                            "type": "message_deleted",
                            "message_id": message_id,
                            "channel_id": channel_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted message_deleted to channel {channel_id}")

            # Reaction events
            elif event_type == "reaction_added":
                channel_id = data.get("channel_id")
                message_id = data.get("message_id")
                reaction = data.get("reaction")

                if channel_id and message_id:
                    await websocket_manager.broadcast_to_channel(
                        channel_id,
                        {
                            "type": "reaction_added",
                            "message_id": message_id,
                            "reaction": reaction,
                            "channel_id": channel_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted reaction_added to channel {channel_id}")

            elif event_type == "reaction_removed":
                channel_id = data.get("channel_id")
                message_id = data.get("message_id")
                reaction = data.get("reaction")

                if channel_id and message_id:
                    await websocket_manager.broadcast_to_channel(
                        channel_id,
                        {
                            "type": "reaction_removed",
                            "message_id": message_id,
                            "reaction": reaction,
                            "channel_id": channel_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted reaction_removed to channel {channel_id}")

            # Presence events
            elif event_type == "user_presence":
                guild_id = data.get("guild_id")
                user_id = data.get("user_id")
                status = data.get("status")

                if guild_id and user_id:
                    # Update local presence cache
                    if status == "online":
                        await presence_service.set_user_online(user_id, guild_id, status)
                    else:
                        await presence_service.set_user_offline(user_id, guild_id)

                    # Broadcast to local WebSocket connections
                    await websocket_manager.broadcast_to_guild(
                        guild_id,
                        {
                            "type": "presence_update",
                            "user_id": user_id,
                            "status": status,
                            "guild_id": guild_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted user_presence to guild {guild_id}")

            elif event_type == "typing_indicator":
                channel_id = data.get("channel_id")
                user_id = data.get("user_id")
                username = data.get("username")
                action = data.get("action")

                if channel_id and user_id:
                    if action == "start":
                        # Store in local Redis
                        typing_key = f"typing:channel:{channel_id}"
                        typing_data = {
                            "user_id": user_id,
                            "username": username,
                            "channel_id": channel_id,
                            "started_at": datetime.utcnow().isoformat()
                        }
                        await self.redis_client.hset(typing_key, str(user_id), json.dumps(typing_data))
                        await self.redis_client.expire(typing_key, 10)
                    else:
                        typing_key = f"typing:channel:{channel_id}"
                        await self.redis_client.hdel(typing_key, str(user_id))

                    # Broadcast to local channel
                    await websocket_manager.broadcast_to_channel(
                        channel_id,
                        {
                            "type": "user_typing",
                            "user_id": user_id,
                            "username": username,
                            "channel_id": channel_id,
                            "action": action,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted typing_indicator to channel {channel_id}")

            # Guild member events
            elif event_type == "member_join":
                guild_id = data.get("guild_id")
                member = data.get("member")

                if guild_id and member:
                    await websocket_manager.broadcast_to_guild(
                        guild_id,
                        {
                            "type": "member_joined",
                            "member": member,
                            "guild_id": guild_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted member_join to guild {guild_id}")

            elif event_type == "member_leave":
                guild_id = data.get("guild_id")
                user_id = data.get("user_id")

                if guild_id and user_id:
                    await websocket_manager.broadcast_to_guild(
                        guild_id,
                        {
                            "type": "member_left",
                            "user_id": user_id,
                            "guild_id": guild_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted member_leave to guild {guild_id}")

            # Channel events
            elif event_type == "channel_created":
                guild_id = data.get("guild_id")
                channel = data.get("channel")

                if guild_id and channel:
                    await websocket_manager.broadcast_to_guild(
                        guild_id,
                        {
                            "type": "channel_created",
                            "channel": channel,
                            "guild_id": guild_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted channel_created to guild {guild_id}")

            elif event_type == "channel_updated":
                guild_id = data.get("guild_id")
                channel_id = data.get("channel_id")
                channel = data.get("channel")

                if guild_id and channel_id:
                    await websocket_manager.broadcast_to_guild(
                        guild_id,
                        {
                            "type": "channel_updated",
                            "channel_id": channel_id,
                            "channel": channel,
                            "guild_id": guild_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted channel_updated to guild {guild_id}")

            elif event_type == "channel_deleted":
                guild_id = data.get("guild_id")
                channel_id = data.get("channel_id")

                if guild_id and channel_id:
                    await websocket_manager.broadcast_to_guild(
                        guild_id,
                        {
                            "type": "channel_deleted",
                            "channel_id": channel_id,
                            "guild_id": guild_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted channel_deleted to guild {guild_id}")

            # Role events
            elif event_type == "role_created":
                guild_id = data.get("guild_id")
                role = data.get("role")

                if guild_id and role:
                    await websocket_manager.broadcast_to_guild(
                        guild_id,
                        {
                            "type": "role_created",
                            "role": role,
                            "guild_id": guild_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted role_created to guild {guild_id}")

            elif event_type == "role_updated":
                guild_id = data.get("guild_id")
                role_id = data.get("role_id")
                role = data.get("role")

                if guild_id and role_id:
                    await websocket_manager.broadcast_to_guild(
                        guild_id,
                        {
                            "type": "role_updated",
                            "role_id": role_id,
                            "role": role,
                            "guild_id": guild_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted role_updated to guild {guild_id}")

            elif event_type == "role_deleted":
                guild_id = data.get("guild_id")
                role_id = data.get("role_id")

                if guild_id and role_id:
                    await websocket_manager.broadcast_to_guild(
                        guild_id,
                        {
                            "type": "role_deleted",
                            "role_id": role_id,
                            "guild_id": guild_id,
                            "timestamp": timestamp
                        }
                    )
                    logger.debug(f"Broadcasted role_deleted to guild {guild_id}")

            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error handling Redis message: {e}", exc_info=True)

    async def listen(self):
        """Listen for Redis messages"""
        if not self.pubsub:
            await self._ensure_connection()

        self.running = True
        logger.info("Redis subscriber started listening")

        try:
            while self.running:
                try:
                    message = await self.pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=1.0
                    )

                    if message and message.get('type') == 'message':
                        channel = message.get('channel')
                        data = message.get('data')

                        if channel and data:
                            try:
                                message_data = json.loads(data)
                                await self._handle_message(channel, message_data)
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse Redis message: {e}")
                            except Exception as e:
                                logger.error(f"Error processing Redis message: {e}")

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in Redis listener: {e}")
                    await asyncio.sleep(1)

        finally:
            logger.info("Redis subscriber stopped")

    async def start(self):
        """Start the Redis subscriber in the background"""
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self.listen())
            logger.info("Redis subscriber task started")

    async def stop(self):
        """Stop the Redis subscriber"""
        self.running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self.pubsub:
            await self.pubsub.close()

        logger.info("Redis subscriber stopped")


# Global subscriber instance
redis_subscriber = RedisEventSubscriber()