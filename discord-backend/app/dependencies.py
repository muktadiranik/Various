# app/api/dependencies.py
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.core.database import get_db_session
from app.core.redis_client import get_redis
from app.core.security import verify_token, create_access_token
from app.repositories.user_repo import UserRepository
from app.repositories.guild_repo import GuildRepository
from app.repositories.channel_repo import ChannelRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.guild_service import GuildService
from app.services.channel_service import ChannelService
from app.services.message_service import MessageService
from app.services.role_service import RoleService
from app.services.permission_service import PermissionService
from app.services.websocket_service import WebSocketService
from app.services.presence_service import PresenceService, presence_service
from app.core.websocket_manager import WebSocketManager, websocket_manager
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


# Database dependency
async def get_db() -> AsyncSession: # type: ignore
    """Get database session"""
    async for session in get_db_session():
        try:
            yield session
        finally:
            await session.close()


# Redis dependency
async def get_redis_client() -> Redis:
    """Get Redis client"""
    return await get_redis()


# Authentication dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    token = credentials.credentials
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user_repo = UserRepository(db)
    user = await user_repo.get(int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "discriminator": user.discriminator,
        "is_bot": user.is_bot
    }


async def get_current_user_ws(
    token: str,
    db: AsyncSession
) -> Optional[Dict[str, Any]]:
    """Get current user for WebSocket connections"""
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    user_repo = UserRepository(db)
    user = await user_repo.get(int(user_id))
    
    if not user or not user.is_active:
        return None
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "discriminator": user.discriminator,
        "is_bot": user.is_bot
    }


async def get_current_user_permissions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    guild_id: Optional[int] = None,
    channel_id: Optional[int] = None
) -> int:
    """Get current user's permissions for a specific guild or channel"""
    from app.services.permission_service import PermissionService
    from app.repositories.member_repo import MemberRepository
    from app.repositories.role_repo import RoleRepository
    from app.repositories.channel_repo import ChannelRepository
    
    member_repo = MemberRepository(db)
    role_repo = RoleRepository(db)
    channel_repo = ChannelRepository(db)
    permission_service = PermissionService(db, member_repo, role_repo, channel_repo)
    
    if guild_id:
        return await permission_service.get_user_guild_permissions(
            current_user["id"],
            guild_id
        )
    elif channel_id:
        return await permission_service.get_user_channel_permissions(
            current_user["id"],
            channel_id
        )
    
    return 0


# Repository dependencies
async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Get user repository"""
    return UserRepository(db)


async def get_guild_repo(db: AsyncSession = Depends(get_db)) -> GuildRepository:
    """Get guild repository"""
    return GuildRepository(db)


async def get_channel_repo(db: AsyncSession = Depends(get_db)) -> ChannelRepository:
    """Get channel repository"""
    return ChannelRepository(db)


async def get_message_repo(db: AsyncSession = Depends(get_db)) -> MessageRepository:
    """Get message repository"""
    return MessageRepository(db)


async def get_member_repo(db: AsyncSession = Depends(get_db)) -> MemberRepository:
    """Get member repository"""
    return MemberRepository(db)


async def get_role_repo(db: AsyncSession = Depends(get_db)) -> RoleRepository:
    """Get role repository"""
    return RoleRepository(db)


# Service dependencies
async def get_auth_service(
    db: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repo)
) -> AuthService:
    """Get auth service"""
    return AuthService(db, user_repo)


async def get_user_service(
    db: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repo)
) -> UserService:
    """Get user service"""
    return UserService(db, user_repo)


async def get_guild_service(
    db: AsyncSession = Depends(get_db),
    guild_repo: GuildRepository = Depends(get_guild_repo),
    member_repo: MemberRepository = Depends(get_member_repo),
    role_repo: RoleRepository = Depends(get_role_repo)
) -> GuildService:
    """Get guild service"""
    return GuildService(db, guild_repo, member_repo, role_repo)


async def get_channel_service(
    db: AsyncSession = Depends(get_db),
    channel_repo: ChannelRepository = Depends(get_channel_repo),
    guild_repo: GuildRepository = Depends(get_guild_repo)
) -> ChannelService:
    """Get channel service"""
    return ChannelService(db, channel_repo, guild_repo)


async def get_message_service(
    db: AsyncSession = Depends(get_db),
    message_repo: MessageRepository = Depends(get_message_repo),
    channel_repo: ChannelRepository = Depends(get_channel_repo),
    user_repo: UserRepository = Depends(get_user_repo)
) -> MessageService:
    """Get message service"""
    return MessageService(db, message_repo, channel_repo, user_repo)


async def get_role_service(
    db: AsyncSession = Depends(get_db),
    role_repo: RoleRepository = Depends(get_role_repo),
    guild_repo: GuildRepository = Depends(get_guild_repo),
    member_repo: MemberRepository = Depends(get_member_repo)
) -> RoleService:
    """Get role service"""
    return RoleService(db, role_repo, guild_repo, member_repo)


async def get_permission_service(
    db: AsyncSession = Depends(get_db),
    member_repo: MemberRepository = Depends(get_member_repo),
    role_repo: RoleRepository = Depends(get_role_repo),
    channel_repo: ChannelRepository = Depends(get_channel_repo)
) -> PermissionService:
    """Get permission service"""
    return PermissionService(db, member_repo, role_repo, channel_repo)


async def get_websocket_service(
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),
    message_service: MessageService = Depends(get_message_service),
    permission_service: PermissionService = Depends(get_permission_service)
) -> WebSocketService:
    """Get websocket service"""
    return WebSocketService(db, redis_client, message_service, permission_service)


async def get_websocket_manager() -> WebSocketManager:
    """Get WebSocket manager singleton"""
    return websocket_manager


async def get_presence_service() -> PresenceService:
    """Get presence service"""
    return presence_service


# Optional user (for public endpoints)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise None"""
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    user_repo = UserRepository(db)
    user = await user_repo.get(int(user_id))
    
    if not user or not user.is_active:
        return None
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "discriminator": user.discriminator,
        "is_bot": user.is_bot
    }