# app/services/role_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.role_repo import RoleRepository
from app.repositories.guild_repo import GuildRepository
from app.repositories.member_repo import MemberRepository
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.core.permissions import Permission, PermissionCalculator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RoleService:
    def __init__(
        self,
        session: AsyncSession,
        role_repo: RoleRepository,
        guild_repo: GuildRepository,
        member_repo: MemberRepository
    ):
        self.session = session
        self.role_repo = role_repo
        self.guild_repo = guild_repo
        self.member_repo = member_repo
    
    async def create_role(
        self,
        guild_id: int,
        user_id: int,
        user_permissions: int,
        role_data: RoleCreate
    ) -> RoleResponse:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_ROLES)
        if not has_manage:
            raise PermissionError("You don't have permission to manage roles")
        
        if await self.role_repo.role_exists(guild_id, role_data.name):
            raise ValueError(f"Role with name '{role_data.name}' already exists")
        
        role = await self.role_repo.create_role(
            guild_id=guild_id,
            name=role_data.name,
            permissions=role_data.permissions,
            position=role_data.position,
            is_mentionable=role_data.is_mentionable,
            is_hoisted=role_data.is_hoisted
        )
        
        await self.session.commit()
        
        return RoleResponse(
            id=role.id,
            name=role.name,
            guild_id=role.guild_id,
            permissions=role.permissions,
            position=role.position,
            is_mentionable=role.is_mentionable,
            is_hoisted=role.is_hoisted,
            created_at=role.created_at,
            updated_at=role.updated_at,
            member_count=0
        )
    
    async def update_role(
        self,
        role_id: int,
        user_id: int,
        user_permissions: int,
        role_data: RoleUpdate
    ) -> Optional[RoleResponse]:
        role = await self.role_repo.get(role_id)
        if not role:
            return None
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_ROLES)
        if not has_manage:
            raise PermissionError("You don't have permission to manage roles")
        
        if role.name == "@everyone" and role_data.name is not None:
            raise PermissionError("Cannot rename @everyone role")
        
        update_data = role_data.dict(exclude_unset=True)
        updated_role = await self.role_repo.update(role_id, **update_data)
        await self.session.commit()
        
        if not updated_role:
            return None
        
        members = await self.role_repo.get_role_members(role_id, limit=1000)
        
        return RoleResponse(
            id=updated_role.id,
            name=updated_role.name,
            guild_id=updated_role.guild_id,
            permissions=updated_role.permissions,
            position=updated_role.position,
            is_mentionable=updated_role.is_mentionable,
            is_hoisted=updated_role.is_hoisted,
            created_at=updated_role.created_at,
            updated_at=updated_role.updated_at,
            member_count=len(members)
        )
    
    async def delete_role(self, role_id: int, user_id: int, user_permissions: int) -> bool:
        role = await self.role_repo.get(role_id)
        if not role:
            return False
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_ROLES)
        if not has_manage:
            raise PermissionError("You don't have permission to manage roles")
        
        if role.name == "@everyone":
            raise PermissionError("Cannot delete @everyone role")
        
        result = await self.role_repo.delete_role(role_id)
        await self.session.commit()
        
        return result
    
    async def assign_role(
        self,
        guild_id: int,
        target_user_id: int,
        role_id: int,
        user_id: int,
        user_permissions: int
    ) -> bool:
        role = await self.role_repo.get(role_id)
        if not role or role.guild_id != guild_id:
            raise ValueError("Role not found")
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_ROLES)
        if not has_manage:
            raise PermissionError("You don't have permission to manage roles")
        
        user_highest = await self.role_repo.get_highest_role(guild_id, user_id)
        role_highest = role.position
        
        if user_highest and user_highest.position <= role_highest:
            raise PermissionError("You cannot assign roles higher than or equal to your highest role")
        
        if not await self.member_repo.is_member(guild_id, target_user_id):
            raise ValueError("User is not a member of this guild")
        
        result = await self.member_repo.add_role(guild_id, target_user_id, role_id)
        await self.session.commit()
        
        return result
    
    async def remove_role(
        self,
        guild_id: int,
        target_user_id: int,
        role_id: int,
        user_id: int,
        user_permissions: int
    ) -> bool:
        role = await self.role_repo.get(role_id)
        if not role or role.guild_id != guild_id:
            raise ValueError("Role not found")
        
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_ROLES)
        if not has_manage:
            raise PermissionError("You don't have permission to manage roles")
        
        if role.name == "@everyone":
            raise PermissionError("Cannot remove @everyone role")
        
        result = await self.member_repo.remove_role(guild_id, target_user_id, role_id)
        await self.session.commit()
        
        return result
    
    async def get_guild_roles(
        self,
        guild_id: int,
        user_id: int,
        user_permissions: int
    ) -> List[RoleResponse]:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")
        
        is_member = await self.member_repo.is_member(guild_id, user_id)
        if not is_member:
            raise PermissionError("You must be a member to view roles")
        
        roles_with_count = await self.role_repo.get_roles_with_members_count(guild_id)
        
        return [
            RoleResponse(
                id=role_dict["id"],
                name=role_dict["name"],
                guild_id=guild_id,
                permissions=role_dict["permissions"],
                position=role_dict["position"],
                is_mentionable=role_dict.get("is_mentionable", False),
                is_hoisted=role_dict.get("is_hoisted", False),
                created_at=role_dict.get("created_at", datetime.utcnow()),
                updated_at=role_dict.get("updated_at", datetime.utcnow()),
                member_count=role_dict.get("member_count", 0)
            ) for role_dict in roles_with_count
        ]
    
    async def get_user_roles(self, guild_id: int, target_user_id: int) -> List[RoleResponse]:
        roles = await self.member_repo.get_member_roles(guild_id, target_user_id)
        
        return [
            RoleResponse(
                id=role.id,
                name=role.name,
                guild_id=role.guild_id,
                permissions=role.permissions,
                position=role.position,
                is_mentionable=role.is_mentionable,
                is_hoisted=role.is_hoisted,
                created_at=role.created_at,
                updated_at=role.updated_at,
                member_count=0
            ) for role in roles
        ]