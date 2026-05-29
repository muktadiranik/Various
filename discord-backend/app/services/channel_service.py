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
        """Create a new channel in a guild"""
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")

        # Check if user is owner (owner has all permissions)
        is_owner = guild.owner_id == user_id
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_CHANNELS)

        logger.info(f"Channel creation - User {user_id}, is_owner={is_owner}, has_manage={has_manage}")

        if not is_owner and not has_manage:
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
        """Update a channel"""
        channel = await self.channel_repo.get(channel_id)
        if not channel:
            return None

        # Check if user is owner of the guild
        guild = await self.guild_repo.get(channel.guild_id)
        is_owner = guild.owner_id == user_id if guild else False
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_CHANNELS)

        if not is_owner and not has_manage:
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

    async def delete_channel(
        self,
        channel_id: int,
        user_id: int,
        user_permissions: int
    ) -> bool:
        """Delete a channel"""
        channel = await self.channel_repo.get(channel_id)
        if not channel:
            return False

        # Check if user is owner of the guild
        guild = await self.guild_repo.get(channel.guild_id)
        is_owner = guild.owner_id == user_id if guild else False
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_CHANNELS)

        if not is_owner and not has_manage:
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
        """Get all channels in a guild"""
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")

        # Check if user is a member or guild is public
        is_member = await self._is_guild_member(guild_id, user_id)
        if not is_member and not guild.is_public:
            raise PermissionError("You don't have permission to view this guild")

        channels = await self.channel_repo.get_guild_channels(guild_id)

        # Filter channels based on view permission
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
        """Get channel by ID"""
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
        """Reorder channels in a guild"""
        guild = await self.guild_repo.get(guild_id)
        is_owner = guild.owner_id == user_id if guild else False
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_CHANNELS)

        if not is_owner and not has_manage:
            raise PermissionError("You don't have permission to manage channels")

        result = await self.channel_repo.reorder_channels(guild_id, channel_ids)
        await self.session.commit()

        return result

    async def get_channel_with_permissions(
        self,
        channel_id: int,
        user_id: int,
        user_permissions: int
    ) -> Optional[ChannelResponse]:
        """Get channel with permission check"""
        channel = await self.channel_repo.get_with_permissions(channel_id)
        if not channel:
            return None

        # Check if user has view permission
        if channel.is_private:
            has_view = PermissionCalculator.has_permission(user_permissions, Permission.VIEW_CHANNEL)
            if not has_view:
                raise PermissionError("You don't have permission to view this channel")

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

    async def _is_guild_member(self, guild_id: int, user_id: int) -> bool:
        """Check if user is a member of the guild"""
        from app.repositories.member_repo import MemberRepository
        member_repo = MemberRepository(self.session)
        return await member_repo.is_member(guild_id, user_id)

    async def get_channel_count(self, guild_id: int) -> int:
        """Get channel count in a guild"""
        return await self.channel_repo.get_channel_count(guild_id)

    async def get_channels_by_parent(self, parent_id: int) -> List[ChannelResponse]:
        """Get child channels of a parent channel"""
        channels = await self.channel_repo.get_channels_by_parent(parent_id)
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
            ) for channel in channels
        ]