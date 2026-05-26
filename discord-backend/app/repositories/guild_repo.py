# app/repositories/guild_repo.py
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.guild import Guild
from app.models.member import GuildMember
from app.models.channel import Channel
from app.models.role import Role
from app.repositories.base import BaseRepository

class GuildRepository(BaseRepository[Guild]):
    def __init__(self, session):
        super().__init__(Guild, session)
    
    async def get_with_members(self, guild_id: int) -> Optional[Guild]:
        """Get guild with its members"""
        result = await self.session.execute(
            select(Guild)
            .where(Guild.id == guild_id)
            .options(
                selectinload(Guild.members)
                .selectinload(GuildMember.user),
                selectinload(Guild.owner)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_with_channels(self, guild_id: int) -> Optional[Guild]:
        """Get guild with its channels"""
        result = await self.session.execute(
            select(Guild)
            .where(Guild.id == guild_id)
            .options(
                selectinload(Guild.channels),
                selectinload(Guild.owner)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_with_roles(self, guild_id: int) -> Optional[Guild]:
        """Get guild with its roles"""
        result = await self.session.execute(
            select(Guild)
            .where(Guild.id == guild_id)
            .options(
                selectinload(Guild.roles),
                selectinload(Guild.owner)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_full_guild(self, guild_id: int) -> Optional[Guild]:
        """Get guild with all related data"""
        result = await self.session.execute(
            select(Guild)
            .where(Guild.id == guild_id)
            .options(
                selectinload(Guild.members)
                .selectinload(GuildMember.user),
                selectinload(Guild.members)
                .selectinload(GuildMember.roles),
                selectinload(Guild.channels),
                selectinload(Guild.roles),
                selectinload(Guild.owner)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_guilds(self, user_id: int) -> List[Guild]:
        """Get all guilds a user is a member of"""
        result = await self.session.execute(
            select(Guild)
            .join(GuildMember, GuildMember.guild_id == Guild.id)
            .where(GuildMember.user_id == user_id)
            .options(
                selectinload(Guild.channels),
                selectinload(Guild.owner)
            )
        )
        return result.scalars().all()
    
    async def get_member_count(self, guild_id: int) -> int:
        """Get member count for a guild"""
        result = await self.session.execute(
            select(func.count())
            .select_from(GuildMember)
            .where(GuildMember.guild_id == guild_id)
        )
        return result.scalar()
    
    async def search_guilds(self, query: str, limit: int = 20) -> List[Guild]:
        """Search public guilds by name"""
        result = await self.session.execute(
            select(Guild)
            .where(
                Guild.name.ilike(f"%{query}%"),
                Guild.is_public == True
            )
            .limit(limit)
        )
        return result.scalars().all()
    
    async def transfer_ownership(self, guild_id: int, new_owner_id: int) -> Optional[Guild]:
        """Transfer guild ownership"""
        return await self.update(guild_id, owner_id=new_owner_id)
    
    async def get_owner(self, guild_id: int) -> Optional[Guild]:
        """Get guild with owner only"""
        result = await self.session.execute(
            select(Guild)
            .where(Guild.id == guild_id)
            .options(selectinload(Guild.owner))
        )
        return result.scalar_one_or_none()