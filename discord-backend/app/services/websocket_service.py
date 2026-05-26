# app/services/websocket_service.py
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.services.message_service import MessageService
from app.services.permission_service import PermissionService
from app.core.websocket_manager import websocket_manager
import logging

logger = logging.getLogger(__name__)

class WebSocketService:
    def __init__(
        self,
        db: AsyncSession,
        redis_client: Optional[Redis],
        message_service: MessageService,
        permission_service: PermissionService
    ):
        self.db = db
        self.redis_client = redis_client
        self.message_service = message_service
        self.permission_service = permission_service
    
    async def broadcast_new_message(
        self,
        channel_id: int,
        message_data: Dict[str, Any],
        sender_connection_id: Optional[str] = None
    ) -> int:
        return await websocket_manager.broadcast_to_channel(
            channel_id,
            {
                "type": "new_message",
                "data": message_data,
                "channel_id": channel_id
            },
            exclude_connection_id=sender_connection_id
        )
    
    async def broadcast_message_update(
        self,
        channel_id: int,
        message_id: int,
        updated_data: Dict[str, Any]
    ) -> int:
        return await websocket_manager.broadcast_to_channel(
            channel_id,
            {
                "type": "message_updated",
                "message_id": message_id,
                "data": updated_data,
                "channel_id": channel_id
            }
        )
    
    async def broadcast_message_delete(self, channel_id: int, message_id: int) -> int:
        return await websocket_manager.broadcast_to_channel(
            channel_id,
            {
                "type": "message_deleted",
                "message_id": message_id,
                "channel_id": channel_id
            }
        )
    
    async def broadcast_typing_indicator(
        self,
        channel_id: int,
        user_id: int,
        username: str,
        action: str
    ) -> int:
        return await websocket_manager.broadcast_to_channel(
            channel_id,
            {
                "type": "user_typing",
                "user_id": user_id,
                "username": username,
                "channel_id": channel_id,
                "action": action
            }
        )
    
    async def send_presence_update(
        self,
        user_id: int,
        status: str,
        guild_id: Optional[int] = None
    ) -> int:
        if guild_id:
            return await websocket_manager.broadcast_to_guild(
                guild_id,
                {
                    "type": "presence_update",
                    "user_id": user_id,
                    "status": status,
                    "guild_id": guild_id
                }
            )
        
        sent_count = 0
        user_guilds = await self.permission_service.get_user_guilds(user_id)
        
        for guild_id in user_guilds:
            sent_count += await websocket_manager.broadcast_to_guild(
                guild_id,
                {
                    "type": "presence_update",
                    "user_id": user_id,
                    "status": status,
                    "guild_id": guild_id
                }
            )
        
        return sent_count