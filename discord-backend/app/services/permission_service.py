# app/services/permission_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.channel_repo import ChannelRepository
from app.repositories.guild_repo import GuildRepository
from app.core.permissions import PermissionCalculator, RoleData, PermissionOverrideData, Permission
import logging

logger = logging.getLogger(__name__)


class PermissionService:
    def __init__(
        self,
        session: AsyncSession,
        member_repo: MemberRepository,
        role_repo: RoleRepository,
        channel_repo: ChannelRepository
    ):
        self.session = session
        self.member_repo = member_repo
        self.role_repo = role_repo
        self.channel_repo = channel_repo
    
    async def get_user_guild_permissions(self, user_id: int, guild_id: int) -> int:
        """Get user's effective permissions in a guild"""
        from app.models.guild import Guild
        
        # Get guild directly using session
        result = await self.session.execute(
            select(Guild).where(Guild.id == guild_id)
        )
        guild = result.scalar_one_or_none()
        
        # Check if user is owner
        if guild and guild.owner_id == user_id:
            logger.info(f"User {user_id} is owner of guild {guild_id}, granting ADMINISTRATOR")
            return Permission.ADMINISTRATOR
        
        # Get user's roles in guild
        member = await self.member_repo.get_member(guild_id, user_id)
        if not member:
            logger.warning(f"User {user_id} is not a member of guild {guild_id}")
            return 0
        
        roles = []
        for role in member.roles:
            roles.append(RoleData(
                id=role.id,
                name=role.name,
                permissions=role.permissions,
                position=role.position
            ))
        
        permissions = PermissionCalculator.calculate_role_permissions(roles)
        logger.debug(f"User {user_id} permissions in guild {guild_id}: {permissions}")
        return permissions
    
    async def get_user_channel_permissions(self, user_id: int, channel_id: int) -> int:
        """Get user's effective permissions in a channel"""
        from app.models.channel import Channel
        from app.models.guild import Guild
        
        # Get channel
        result = await self.session.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        channel = result.scalar_one_or_none()
        
        if not channel:
            return 0
        
        # Get base guild permissions
        guild_permissions = await self.get_user_guild_permissions(user_id, channel.guild_id)
        
        # Check administrator
        if guild_permissions & Permission.ADMINISTRATOR:
            return Permission.all_permissions()
        
        # Get role overrides
        role_overrides = []
        member = await self.member_repo.get_member(channel.guild_id, user_id)
        
        if member:
            for role in member.roles:
                overrides = await self.get_role_overrides_for_channel(role.id, channel_id)
                for override in overrides:
                    role_overrides.append((override.allow, override.deny))
        
        # Get member overrides
        member_overrides = []
        member_override = await self.get_member_override_for_channel(user_id, channel_id)
        if member_override:
            member_overrides.append((member_override.allow, member_override.deny))
        
        return PermissionCalculator.calculate_channel_permissions(
            guild_permissions,
            role_overrides,
            member_overrides
        )
    
    async def get_role_overrides_for_channel(self, role_id: int, channel_id: int):
        """Get permission overrides for a role in a channel"""
        from app.models.permission import PermissionOverride
        
        result = await self.session.execute(
            select(PermissionOverride).where(
                PermissionOverride.role_id == role_id,
                PermissionOverride.channel_id == channel_id
            )
        )
        return result.scalars().all()
    
    async def get_member_override_for_channel(self, user_id: int, channel_id: int):
        """Get permission override for a user in a channel"""
        from app.models.permission import PermissionOverride
        from app.models.member import GuildMember
        
        result = await self.session.execute(
            select(PermissionOverride).join(
                GuildMember, GuildMember.id == PermissionOverride.user_id
            ).where(
                GuildMember.user_id == user_id,
                PermissionOverride.channel_id == channel_id
            )
        )
        return result.scalar_one_or_none()
    
    async def check_guild_membership(self, user_id: int, guild_id: int) -> bool:
        """Check if user is a member of a guild"""
        return await self.member_repo.is_member(guild_id, user_id)
    
    async def get_user_guilds(self, user_id: int) -> List[int]:
        """Get list of guild IDs the user is a member of"""
        memberships = await self.member_repo.get_user_guild_memberships(user_id)
        return [m.guild_id for m in memberships]