# app/repositories/member_repo.py
from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete, and_, func, or_
from sqlalchemy.orm import selectinload, joinedload
from app.models.member import GuildMember, member_roles
from app.models.user import User
from app.models.role import Role
from app.models.guild import Guild
from app.repositories.base import BaseRepository

class MemberRepository(BaseRepository[GuildMember]):
    def __init__(self, session):
        super().__init__(GuildMember, session)
    
    async def get_member(self, guild_id: int, user_id: int) -> Optional[GuildMember]:
        """Get a specific guild member"""
        result = await self.session.execute(
            select(GuildMember)
            .where(
                GuildMember.guild_id == guild_id,
                GuildMember.user_id == user_id
            )
            .options(
                selectinload(GuildMember.user),
                selectinload(GuildMember.roles)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_guild_members(self, guild_id: int, skip: int = 0, limit: int = 100) -> List[GuildMember]:
        """Get all members of a guild"""
        result = await self.session.execute(
            select(GuildMember)
            .where(GuildMember.guild_id == guild_id)
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(GuildMember.user),
                selectinload(GuildMember.roles)
            )
        )
        return result.scalars().all()
    
    async def get_member_with_permissions(self, guild_id: int, user_id: int) -> Optional[GuildMember]:
        """Get member with roles for permission calculation"""
        result = await self.session.execute(
            select(GuildMember)
            .where(
                GuildMember.guild_id == guild_id,
                GuildMember.user_id == user_id
            )
            .options(
                selectinload(GuildMember.user),
                selectinload(GuildMember.roles),
                selectinload(GuildMember.guild)
                .selectinload(Guild.roles)
            )
        )
        return result.scalar_one_or_none()
    
    async def add_member(self, guild_id: int, user_id: int, nickname: Optional[str] = None) -> GuildMember:
        """Add a member to a guild"""
        return await self.create(
            guild_id=guild_id,
            user_id=user_id,
            nickname=nickname
        )
    
    async def remove_member(self, guild_id: int, user_id: int) -> bool:
        """Remove a member from a guild"""
        result = await self.session.execute(
            delete(GuildMember)
            .where(
                GuildMember.guild_id == guild_id,
                GuildMember.user_id == user_id
            )
        )
        await self.session.flush()
        return result.rowcount > 0
    
    async def update_nickname(self, guild_id: int, user_id: int, nickname: str) -> Optional[GuildMember]:
        """Update a member's nickname"""
        member = await self.get_member(guild_id, user_id)
        if member:
            return await self.update(member.id, nickname=nickname)
        return None
    
    async def add_role(self, guild_id: int, user_id: int, role_id: int) -> bool:
        """Add a role to a member"""
        member = await self.get_member(guild_id, user_id)
        if not member:
            return False
        
        await self.session.execute(
            member_roles.insert().values(
                member_id=member.id,
                role_id=role_id
            )
        )
        await self.session.flush()
        return True
    
    async def remove_role(self, guild_id: int, user_id: int, role_id: int) -> bool:
        """Remove a role from a member"""
        member = await self.get_member(guild_id, user_id)
        if not member:
            return False
        
        await self.session.execute(
            member_roles.delete().where(
                and_(
                    member_roles.c.member_id == member.id,
                    member_roles.c.role_id == role_id
                )
            )
        )
        await self.session.flush()
        return True
    
    async def get_member_roles(self, guild_id: int, user_id: int) -> List[Role]:
        """Get all roles of a member"""
        member = await self.get_member(guild_id, user_id)
        if not member:
            return []
        
        result = await self.session.execute(
            select(Role)
            .join(member_roles, member_roles.c.role_id == Role.id)
            .where(member_roles.c.member_id == member.id)
            .order_by(Role.position.desc())
        )
        return result.scalars().all()
    
    async def get_user_guild_memberships(self, user_id: int) -> List[GuildMember]:
        """Get all guild memberships for a user"""
        result = await self.session.execute(
            select(GuildMember)
            .where(GuildMember.user_id == user_id)
            .options(
                selectinload(GuildMember.guild),
                selectinload(GuildMember.roles)
            )
        )
        return result.scalars().all()
    
    async def is_member(self, guild_id: int, user_id: int) -> bool:
        """Check if a user is a member of a guild"""
        return await self.exists(guild_id=guild_id, user_id=user_id)
    
    async def get_members_by_role(self, guild_id: int, role_id: int) -> List[GuildMember]:
        """Get all members with a specific role"""
        result = await self.session.execute(
            select(GuildMember)
            .where(GuildMember.guild_id == guild_id)
            .join(member_roles, member_roles.c.member_id == GuildMember.id)
            .where(member_roles.c.role_id == role_id)
            .options(
                selectinload(GuildMember.user),
                selectinload(GuildMember.roles)
            )
        )
        return result.scalars().all()
    
    async def get_member_count_by_guild(self, guild_id: int) -> int:
        """Get member count for a guild"""
        return await self.count(guild_id=guild_id)
    
    async def bulk_add_members(self, guild_id: int, user_ids: List[int]) -> List[GuildMember]:
        """Bulk add members to a guild"""
        members = []
        for user_id in user_ids:
            existing = await self.get_member(guild_id, user_id)
            if not existing:
                member = await self.add_member(guild_id, user_id)
                members.append(member)
        return members
    
    async def search_members(self, guild_id: int, query: str, limit: int = 50) -> List[GuildMember]:
        """Search members by username or nickname"""
        result = await self.session.execute(
            select(GuildMember)
            .where(GuildMember.guild_id == guild_id)
            .join(User, User.id == GuildMember.user_id)
            .where(
                or_(
                    User.username.ilike(f"%{query}%"),
                    GuildMember.nickname.ilike(f"%{query}%")
                )
            )
            .limit(limit)
            .options(
                selectinload(GuildMember.user),
                selectinload(GuildMember.roles)
            )
        )
        return result.scalars().all()