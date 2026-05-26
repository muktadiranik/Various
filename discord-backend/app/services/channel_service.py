# app/services/channel_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.channel_repo import ChannelRepository
from app.repositories.guild_repo import GuildRepository
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse
from app.core.permissions import Permission, PermissionCalculator
from app.services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)

class ChannelService:
    def __init__(
        self,
        session: AsyncSession,
        channel_repo: ChannelRepository,
        guild_repo: GuildRepository
    ):
        self.session = session
        self.channel_repo = channel_repo
        self.guild_repo = guild_repo
    
    async def create_channel(
        self,
        guild_id: int,
        user_id: int,
        user_permissions: int,
        channel_data: ChannelCreate
    ) -> ChannelResponse:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_CHANNELS)
        if not has_manage:
            raise PermissionError("You don't have permission to manage channels")
        
        if channel_data.parent_id:
            parent = await self.channel_repo.get(channel_data.parent_id)
            if not parent or parent.guild_id != guild_id:
                raise ValueError("Parent channel not found in this guild")
        
        existing = await self.channel_repo.get_channel_by_name(guild_id, channel_data.name)
        if existing:
            raise ValueError(f"Channel with name '{channel_data.name}' already exists")
        
        if channel_data.type == "text":
            channel = await self.channel_repo.create_text_channel(
                guild_id=guild_id,
                name=channel_data.name,
                topic=channel_data.topic,
                parent_id=channel_data.parent_id,
                is_private=channel_data.is_private
            )
        else:
            channel = await self.channel_repo.create_voice_channel(
                guild_id=guild_id,
                name=channel_data.name,
                bitrate=channel_data.bitrate or 64000,
                user_limit=channel_data.user_limit or 0,
                parent_id=channel_data.parent_id,
                is_private=channel_data.is_private
            )
        
        await self.session.commit()
        
        await redis_service.publish_channel_create(
            guild_id=guild_id,
            channel_data={
                "id": channel.id,
                "name": channel.name,
                "type": channel.type,
                "guild_id": channel.guild_id
            }
        )
        
        return ChannelResponse(
            id=channel.id,
            name=channel.name,
            type=channel.type,
            guild_id=channel.guild_id,
            parent_id=channel.parent_id,
            position=channel.position,
            is_private=channel.is_private,
            topic=channel.topic,
            bitrate=channel.bitrate,
            user_limit=channel.user_limit,
            created_at=channel.created_at,
            updated_at=channel.updated_at
        )
    
    async def update_channel(
        self,
        channel_id: int,
        user_id: int,
        user_permissions: int,
        channel_data: ChannelUpdate
    ) -> Optional[ChannelResponse]:
        channel = await self.channel_repo.get(channel_id)
        if not channel:
            return None
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_CHANNELS)
        if not has_manage:
            raise PermissionError("You don't have permission to manage channels")
        
        update_data = channel_data.dict(exclude_unset=True)
        updated_channel = await self.channel_repo.update(channel_id, **update_data)
        await self.session.commit()
        
        if not updated_channel:
            return None
        
        await redis_service.publish_channel_update(
            guild_id=channel.guild_id,
            channel_id=channel_id,
            channel_data={
                "id": updated_channel.id,
                "name": updated_channel.name,
                "type": updated_channel.type
            }
        )
        
        return ChannelResponse(
            id=updated_channel.id,
            name=updated_channel.name,
            type=updated_channel.type,
            guild_id=updated_channel.guild_id,
            parent_id=updated_channel.parent_id,
            position=updated_channel.position,
            is_private=updated_channel.is_private,
            topic=updated_channel.topic,
            bitrate=updated_channel.bitrate,
            user_limit=updated_channel.user_limit,
            created_at=updated_channel.created_at,
            updated_at=updated_channel.updated_at
        )
    
    async def delete_channel(self, channel_id: int, user_id: int, user_permissions: int) -> bool:
        channel = await self.channel_repo.get(channel_id)
        if not channel:
            return False
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_CHANNELS)
        if not has_manage:
            raise PermissionError("You don't have permission to manage channels")
        
        guild_id = channel.guild_id
        result = await self.channel_repo.delete(channel_id)
        await self.session.commit()
        
        if result:
            await redis_service.publish_channel_delete(guild_id, channel_id)
        
        return result
    
    async def get_guild_channels(
        self,
        guild_id: int,
        user_id: int,
        user_permissions: int
    ) -> List[ChannelResponse]:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")
        
        is_member = await self.guild_repo.get_member_count(guild_id) > 0
        if not is_member and not guild.is_public:
            raise PermissionError("You don't have permission to view this guild")
        
        channels = await self.channel_repo.get_guild_channels(guild_id)
        
        visible_channels = []
        for channel in channels:
            if channel.is_private:
                has_view = PermissionCalculator.has_permission(user_permissions, Permission.VIEW_CHANNEL)
                if not has_view:
                    continue
            visible_channels.append(channel)
        
        return [
            ChannelResponse(
                id=channel.id,
                name=channel.name,
                type=channel.type,
                guild_id=channel.guild_id,
                parent_id=channel.parent_id,
                position=channel.position,
                is_private=channel.is_private,
                topic=channel.topic,
                bitrate=channel.bitrate,
                user_limit=channel.user_limit,
                created_at=channel.created_at,
                updated_at=channel.updated_at
            ) for channel in visible_channels
        ]
    
    async def get_channel(self, channel_id: int) -> Optional[ChannelResponse]:
        channel = await self.channel_repo.get(channel_id)
        if not channel:
            return None
        
        return ChannelResponse(
            id=channel.id,
            name=channel.name,
            type=channel.type,
            guild_id=channel.guild_id,
            parent_id=channel.parent_id,
            position=channel.position,
            is_private=channel.is_private,
            topic=channel.topic,
            bitrate=channel.bitrate,
            user_limit=channel.user_limit,
            created_at=channel.created_at,
            updated_at=channel.updated_at
        )
    
    async def reorder_channels(
        self,
        guild_id: int,
        channel_ids: List[int],
        user_id: int,
        user_permissions: int
    ) -> bool:
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_CHANNELS)
        if not has_manage:
            raise PermissionError("You don't have permission to manage channels")
        
        result = await self.channel_repo.reorder_channels(guild_id, channel_ids)
        await self.session.commit()
        
        return result