# app/services/guild_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.guild_repo import GuildRepository
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.channel_repo import ChannelRepository
from app.schemas.guild import GuildCreate, GuildUpdate, GuildResponse, GuildMemberResponse, GuildDetailResponse
from app.schemas.channel import ChannelResponse
from app.schemas.role import RoleResponse
from app.core.permissions import Permission, PermissionCalculator, DEFAULT_EVERYONE_PERMISSIONS
from app.services.redis_service import redis_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GuildService:
    def __init__(
        self,
        session: AsyncSession,
        guild_repo: GuildRepository,
        member_repo: MemberRepository,
        role_repo: RoleRepository
    ):
        self.session = session
        self.guild_repo = guild_repo
        self.member_repo = member_repo
        self.role_repo = role_repo
    
    async def create_guild(self, owner_id: int, guild_data: GuildCreate) -> GuildResponse:
        guild = await self.guild_repo.create(
            name=guild_data.name,
            description=guild_data.description,
            owner_id=owner_id,
            is_public=guild_data.is_public
        )
        
        await self.member_repo.add_member(guild.id, owner_id)
        
        everyone_role = await self.role_repo.create_role(
            guild_id=guild.id,
            name="@everyone",
            permissions=DEFAULT_EVERYONE_PERMISSIONS,
            position=0
        )
        
        admin_role = await self.role_repo.create_role(
            guild_id=guild.id,
            name="Admin",
            permissions=Permission.ADMINISTRATOR,
            position=100
        )
        
        await self.member_repo.add_role(guild.id, owner_id, admin_role.id)
        await self._create_default_channels(guild.id)
        
        await self.session.commit()
        
        await redis_service.publish_channel_create(
            guild_id=guild.id,
            channel_data={"guild_id": guild.id, "action": "created"}
        )
        
        member_count = await self.guild_repo.get_member_count(guild.id)
        
        return GuildResponse(
            id=guild.id,
            name=guild.name,
            description=guild.description,
            icon_url=guild.icon_url,
            owner_id=guild.owner_id,
            owner_username="",
            is_public=guild.is_public,
            member_count=member_count,
            created_at=guild.created_at,
            updated_at=guild.updated_at
        )
    
    async def _create_default_channels(self, guild_id: int):
        channel_repo = ChannelRepository(self.session)
        
        await channel_repo.create_text_channel(
            guild_id=guild_id,
            name="general",
            topic="General discussion"
        )
        
        await channel_repo.create_voice_channel(
            guild_id=guild_id,
            name="General Voice",
            bitrate=64000
        )
    
    async def get_guild(self, guild_id: int) -> Optional[GuildResponse]:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            return None
        
        member_count = await self.guild_repo.get_member_count(guild_id)
        
        return GuildResponse(
            id=guild.id,
            name=guild.name,
            description=guild.description,
            icon_url=guild.icon_url,
            owner_id=guild.owner_id,
            owner_username="",
            is_public=guild.is_public,
            member_count=member_count,
            created_at=guild.created_at,
            updated_at=guild.updated_at
        )
    
    async def get_guild_detail(self, guild_id: int, user_id: int) -> Optional[GuildDetailResponse]:
        guild = await self.guild_repo.get_full_guild(guild_id)
        if not guild:
            return None
        
        is_member = await self.member_repo.is_member(guild_id, user_id)
        if not is_member and not guild.is_public:
            return None
        
        member_count = await self.guild_repo.get_member_count(guild_id)
        
        channels = [
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
            ) for channel in guild.channels
        ]
        
        roles = [
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
            ) for role in guild.roles
        ]
        
        return GuildDetailResponse(
            id=guild.id,
            name=guild.name,
            description=guild.description,
            icon_url=guild.icon_url,
            owner_id=guild.owner_id,
            owner_username=guild.owner.username if guild.owner else "",
            is_public=guild.is_public,
            member_count=member_count,
            created_at=guild.created_at,
            updated_at=guild.updated_at,
            channels=channels,
            roles=roles
        )
    
    async def update_guild(
        self,
        guild_id: int,
        user_id: int,
        user_permissions: int,
        guild_data: GuildUpdate
    ) -> Optional[GuildResponse]:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            return None
        
        is_owner = guild.owner_id == user_id
        has_manage = PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_GUILD)
        
        if not is_owner and not has_manage:
            raise PermissionError("You don't have permission to manage this guild")
        
        update_data = guild_data.dict(exclude_unset=True)
        updated_guild = await self.guild_repo.update(guild_id, **update_data)
        await self.session.commit()
        
        if not updated_guild:
            return None
        
        member_count = await self.guild_repo.get_member_count(guild_id)
        
        return GuildResponse(
            id=updated_guild.id,
            name=updated_guild.name,
            description=updated_guild.description,
            icon_url=updated_guild.icon_url,
            owner_id=updated_guild.owner_id,
            owner_username="",
            is_public=updated_guild.is_public,
            member_count=member_count,
            created_at=updated_guild.created_at,
            updated_at=updated_guild.updated_at
        )
    
    async def delete_guild(self, guild_id: int, user_id: int, user_permissions: int) -> bool:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            return False
        
        is_owner = guild.owner_id == user_id
        has_admin = PermissionCalculator.has_permission(user_permissions, Permission.ADMINISTRATOR)
        
        if not is_owner and not has_admin:
            raise PermissionError("Only guild owner can delete the guild")
        
        result = await self.guild_repo.delete(guild_id)
        await self.session.commit()
        
        return result
    
    async def join_guild(self, guild_id: int, user_id: int) -> bool:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")
        
        if await self.member_repo.is_member(guild_id, user_id):
            raise ValueError("Already a member of this guild")
        
        if not guild.is_public:
            raise PermissionError("Cannot join private guild")
        
        await self.member_repo.add_member(guild_id, user_id)
        
        everyone_role = await self.role_repo.get_default_role(guild_id)
        if everyone_role:
            await self.member_repo.add_role(guild_id, user_id, everyone_role.id)
        
        await self.session.commit()
        
        await redis_service.publish_guild_member_join(
            guild_id=guild_id,
            member_data={"user_id": user_id, "action": "joined"}
        )
        
        return True
    
    async def leave_guild(self, guild_id: int, user_id: int) -> bool:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")
        
        if not await self.member_repo.is_member(guild_id, user_id):
            raise ValueError("Not a member of this guild")
        
        if guild.owner_id == user_id:
            raise PermissionError("Owner cannot leave guild. Transfer ownership first")
        
        result = await self.member_repo.remove_member(guild_id, user_id)
        await self.session.commit()
        
        await redis_service.publish_guild_member_leave(guild_id, user_id)
        
        return result
    
    async def get_guild_members(
        self,
        guild_id: int,
        user_id: int,
        user_permissions: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[GuildMemberResponse]:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")
        
        is_member = await self.member_repo.is_member(guild_id, user_id)
        if not is_member:
            raise PermissionError("You must be a member to view member list")
        
        members = await self.member_repo.get_guild_members(guild_id, skip, limit)
        
        member_responses = []
        for member in members:
            member_responses.append(GuildMemberResponse(
                user_id=member.user.id,
                username=member.user.username,
                discriminator=member.user.discriminator,
                avatar_url=member.user.avatar_url,
                nickname=member.nickname,
                joined_at=member.joined_at,
                roles=[
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
                    ) for role in member.roles
                ]
            ))
        
        return member_responses
    
    async def kick_member(
        self,
        guild_id: int,
        target_user_id: int,
        user_id: int,
        user_permissions: int
    ) -> bool:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")
        
        has_kick = PermissionCalculator.has_permission(user_permissions, Permission.KICK_MEMBERS)
        if not has_kick:
            raise PermissionError("You don't have permission to kick members")
        
        if guild.owner_id == target_user_id:
            raise PermissionError("Cannot kick the guild owner")
        
        if target_user_id == user_id:
            raise PermissionError("Cannot kick yourself")
        
        if not await self.member_repo.is_member(guild_id, target_user_id):
            raise ValueError("User is not a member")
        
        result = await self.member_repo.remove_member(guild_id, target_user_id)
        await self.session.commit()
        
        return result
    
    async def transfer_ownership(
        self,
        guild_id: int,
        new_owner_id: int,
        user_id: int,
        user_permissions: int
    ) -> bool:
        guild = await self.guild_repo.get(guild_id)
        if not guild:
            raise ValueError("Guild not found")
        
        if guild.owner_id != user_id:
            raise PermissionError("Only guild owner can transfer ownership")
        
        if not await self.member_repo.is_member(guild_id, new_owner_id):
            raise ValueError("New owner must be a member of the guild")
        
        updated_guild = await self.guild_repo.transfer_ownership(guild_id, new_owner_id)
        await self.session.commit()
        
        return updated_guild is not None
    
    async def get_user_guilds(self, user_id: int) -> List[GuildResponse]:
        guilds = await self.guild_repo.get_user_guilds(user_id)
        
        guild_responses = []
        for guild in guilds:
            member_count = await self.guild_repo.get_member_count(guild.id)
            guild_responses.append(GuildResponse(
                id=guild.id,
                name=guild.name,
                description=guild.description,
                icon_url=guild.icon_url,
                owner_id=guild.owner_id,
                owner_username=guild.owner.username if guild.owner else "",
                is_public=guild.is_public,
                member_count=member_count,
                created_at=guild.created_at,
                updated_at=guild.updated_at
            ))
        
        return guild_responses