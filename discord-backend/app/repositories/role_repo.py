# app/repositories/role_repo.py
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import selectinload, joinedload
from app.models.role import Role
from app.models.permission import PermissionOverride, PermissionOverrideType
from app.models.member import member_roles
from app.repositories.base import BaseRepository
from datetime import datetime

class RoleRepository(BaseRepository[Role]):
    def __init__(self, session):
        super().__init__(Role, session)
    
    async def get_guild_roles(self, guild_id: int) -> List[Role]:
        """Get all roles in a guild"""
        result = await self.session.execute(
            select(Role)
            .where(Role.guild_id == guild_id)
            .order_by(Role.position.desc())
        )
        return result.scalars().all()
    
    async def get_role_with_permissions(self, role_id: int) -> Optional[Role]:
        """Get role with permission overrides"""
        result = await self.session.execute(
            select(Role)
            .where(Role.id == role_id)
            .options(
                selectinload(Role.permission_overrides),
                selectinload(Role.members)
                .selectinload(Role.members.entities.user)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_default_role(self, guild_id: int) -> Optional[Role]:
        """Get the @everyone role for a guild"""
        result = await self.session.execute(
            select(Role)
            .where(
                Role.guild_id == guild_id,
                Role.name == "@everyone"
            )
        )
        return result.scalar_one_or_none()
    
    async def create_role(self, guild_id: int, name: str, permissions: int = 0, **kwargs) -> Role:
        """Create a new role"""
        return await self.create(
            guild_id=guild_id,
            name=name,
            permissions=permissions,
            **kwargs
        )
    
    async def update_role_permissions(self, role_id: int, permissions: int) -> Optional[Role]:
        """Update role permissions"""
        return await self.update(role_id, permissions=permissions)
    
    async def update_role_position(self, role_id: int, position: int) -> Optional[Role]:
        """Update role position"""
        return await self.update(role_id, position=position)
    
    async def delete_role(self, role_id: int) -> bool:
        """Delete a role (cannot delete @everyone)"""
        role = await self.get(role_id)
        if not role or role.name == "@everyone":
            return False
        
        return await self.delete(role_id)
    
    async def get_role_members(self, role_id: int, skip: int = 0, limit: int = 100) -> List:
        """Get members with a specific role"""
        from app.models.member import GuildMember
        
        result = await self.session.execute(
            select(GuildMember)
            .join(member_roles, member_roles.c.member_id == GuildMember.id)
            .where(member_roles.c.role_id == role_id)
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(GuildMember.user),
                selectinload(GuildMember.roles)
            )
        )
        return result.scalars().all()
    
    async def get_role_permission_overrides(self, role_id: int) -> List[PermissionOverride]:
        """Get all permission overrides for a role"""
        result = await self.session.execute(
            select(PermissionOverride)
            .where(PermissionOverride.role_id == role_id)
            .options(
                selectinload(PermissionOverride.channel)
            )
        )
        return result.scalars().all()
    
    async def get_roles_by_permission(self, guild_id: int, permission_bit: int) -> List[Role]:
        """Get roles that have a specific permission"""
        result = await self.session.execute(
            select(Role)
            .where(
                Role.guild_id == guild_id,
                Role.permissions.op("&")(permission_bit) == permission_bit
            )
            .order_by(Role.position.desc())
        )
        return result.scalars().all()
    
    async def reorder_roles(self, guild_id: int, role_ids: List[int]) -> bool:
        """Reorder roles in a guild"""
        for position, role_id in enumerate(role_ids):
            await self.session.execute(
                update(Role)
                .where(Role.id == role_id, Role.guild_id == guild_id)
                .values(position=position)
            )
        await self.session.flush()
        return True
    
    async def get_highest_role(self, guild_id: int, user_id: int) -> Optional[Role]:
        """Get the highest role of a user in a guild"""
        from app.models.member import GuildMember
        
        result = await self.session.execute(
            select(Role)
            .join(member_roles, member_roles.c.role_id == Role.id)
            .join(GuildMember, GuildMember.id == member_roles.c.member_id)
            .where(
                GuildMember.guild_id == guild_id,
                GuildMember.user_id == user_id
            )
            .order_by(Role.position.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_roles_with_members_count(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get roles with member count"""
        result = await self.session.execute(
            select(
                Role.id,
                Role.name,
                Role.permissions,
                Role.position,
                Role.is_mentionable,
                Role.is_hoisted,
                Role.created_at,
                Role.updated_at,
                func.count(member_roles.c.member_id).label("member_count")
            )
            .outerjoin(member_roles, member_roles.c.role_id == Role.id)
            .where(Role.guild_id == guild_id)
            .group_by(Role.id)
            .order_by(Role.position.desc())
        )
        return [dict(row._mapping) for row in result.all()]
    
    async def role_exists(self, guild_id: int, name: str) -> bool:
        """Check if a role exists in a guild"""
        return await self.exists(guild_id=guild_id, name=name)
    
    async def duplicate_role(self, source_role_id: int, new_name: str) -> Optional[Role]:
        """Duplicate a role with all its permissions"""
        source_role = await self.get(source_role_id)
        if not source_role:
            return None
        
        new_role = await self.create_role(
            guild_id=source_role.guild_id,
            name=new_name,
            permissions=source_role.permissions,
            position=source_role.position + 1,
            is_mentionable=source_role.is_mentionable,
            is_hoisted=source_role.is_hoisted
        )
        
        overrides = await self.get_role_permission_overrides(source_role_id)
        for override in overrides:
            await self.session.execute(
                PermissionOverride.__table__.insert().values(
                    channel_id=override.channel_id,
                    role_id=new_role.id,
                    user_id=None,
                    allow=override.allow,
                    deny=override.deny,
                    override_type=override.override_type
                )
            )
        
        await self.session.flush()
        return new_role