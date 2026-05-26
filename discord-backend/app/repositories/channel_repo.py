# app/repositories/channel_repo.py
from typing import Optional, List
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from app.models.channel import Channel, ChannelType
from app.models.permission import PermissionOverride
from app.repositories.base import BaseRepository

class ChannelRepository(BaseRepository[Channel]):
    def __init__(self, session):
        super().__init__(Channel, session)
    
    async def get_guild_channels(self, guild_id: int) -> List[Channel]:
        """Get all channels in a guild"""
        result = await self.session.execute(
            select(Channel)
            .where(Channel.guild_id == guild_id)
            .order_by(Channel.position, Channel.created_at)
        )
        return result.scalars().all()
    
    async def get_text_channels(self, guild_id: int) -> List[Channel]:
        """Get all text channels in a guild"""
        result = await self.session.execute(
            select(Channel)
            .where(
                Channel.guild_id == guild_id,
                Channel.type == ChannelType.TEXT
            )
            .order_by(Channel.position)
        )
        return result.scalars().all()
    
    async def get_voice_channels(self, guild_id: int) -> List[Channel]:
        """Get all voice channels in a guild"""
        result = await self.session.execute(
            select(Channel)
            .where(
                Channel.guild_id == guild_id,
                Channel.type == ChannelType.VOICE
            )
            .order_by(Channel.position)
        )
        return result.scalars().all()
    
    async def get_with_permissions(self, channel_id: int) -> Optional[Channel]:
        """Get channel with permission overrides and guild roles"""
        from app.models.guild import Guild
        
        result = await self.session.execute(
            select(Channel)
            .where(Channel.id == channel_id)
            .options(
                selectinload(Channel.permission_overrides),
                selectinload(Channel.guild)
                .selectinload(Guild.roles),
                selectinload(Channel.parent)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_channels_by_parent(self, parent_id: int) -> List[Channel]:
        """Get child channels of a parent channel"""
        result = await self.session.execute(
            select(Channel)
            .where(Channel.parent_id == parent_id)
            .order_by(Channel.position)
        )
        return result.scalars().all()
    
    async def reorder_channels(self, guild_id: int, channel_ids: List[int]) -> bool:
        """Reorder channels in a guild"""
        for position, channel_id in enumerate(channel_ids):
            await self.session.execute(
                update(Channel)
                .where(Channel.id == channel_id, Channel.guild_id == guild_id)
                .values(position=position)
            )
        await self.session.flush()
        return True
    
    async def get_channel_count(self, guild_id: int) -> int:
        """Get channel count in a guild"""
        result = await self.session.execute(
            select(func.count())
            .select_from(Channel)
            .where(Channel.guild_id == guild_id)
        )
        return result.scalar()
    
    async def get_channel_by_name(self, guild_id: int, name: str) -> Optional[Channel]:
        """Get channel by name in a guild"""
        result = await self.session.execute(
            select(Channel)
            .where(
                Channel.guild_id == guild_id,
                Channel.name == name
            )
        )
        return result.scalar_one_or_none()
    
    async def create_voice_channel(
        self, 
        guild_id: int, 
        name: str, 
        bitrate: int = 64000, 
        user_limit: int = 0, 
        **kwargs
    ) -> Channel:
        """Create a voice channel"""
        return await self.create(
            guild_id=guild_id,
            name=name,
            type=ChannelType.VOICE,
            bitrate=bitrate,
            user_limit=user_limit,
            **kwargs
        )
    
    async def create_text_channel(
        self, 
        guild_id: int, 
        name: str, 
        topic: Optional[str] = None, 
        **kwargs
    ) -> Channel:
        """Create a text channel"""
        return await self.create(
            guild_id=guild_id,
            name=name,
            type=ChannelType.TEXT,
            topic=topic,
            **kwargs
        )
    
    async def get_channel_with_messages(self, channel_id: int, limit: int = 50) -> Optional[Channel]:
        """Get channel with recent messages"""
        from app.models.message import Message
        
        result = await self.session.execute(
            select(Channel)
            .where(Channel.id == channel_id)
            .options(
                selectinload(Channel.messages)
                .limit(limit)
                .order_by(Message.created_at.desc())
                .options(selectinload(Message.author))
            )
        )
        return result.scalar_one_or_none()