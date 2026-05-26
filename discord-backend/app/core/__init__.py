# app/core/__init__.py
from .security import (
    hash_password,
    verify_password,
    create_token,
    verify_token,
    create_access_token,
    create_refresh_token,
    get_user_permissions
)
from .exceptions import (
    DiscordException,
    PermissionDenied,
    NotFoundError,
    ValidationError,
    ConflictError
)
from .constants import (
    Permission,
    DEFAULT_EVERYONE_PERMISSIONS,
    DEFAULT_ADMIN_PERMISSIONS,
    DEFAULT_MODERATOR_PERMISSIONS,
    ADMIN_ROLE_POSITION,
    MODERATOR_ROLE_POSITION,
    DEFAULT_ROLE_POSITION,
    TEXT_CHANNEL_PERMISSIONS,
    VOICE_CHANNEL_PERMISSIONS,
    GUEST_PERMISSIONS,
    MEMBER_PERMISSIONS
)
from .websocket_manager import WebSocketManager, websocket_manager, ConnectionInfo
from .redis_client import get_redis, close_redis
from .database import get_db_session, init_db, close_db, engine, AsyncSessionLocal
from .permissions import (
    PermissionCalculator,
    PermissionValidator,
    RoleData,
    PermissionOverrideData
)

__all__ = [
    # Security
    "hash_password",
    "verify_password",
    "create_token",
    "verify_token",
    "create_access_token",
    "create_refresh_token",
    "get_user_permissions",
    
    # Exceptions
    "DiscordException",
    "PermissionDenied",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    
    # Constants
    "Permission",
    "DEFAULT_EVERYONE_PERMISSIONS",
    "DEFAULT_ADMIN_PERMISSIONS",
    "DEFAULT_MODERATOR_PERMISSIONS",
    "ADMIN_ROLE_POSITION",
    "MODERATOR_ROLE_POSITION",
    "DEFAULT_ROLE_POSITION",
    "TEXT_CHANNEL_PERMISSIONS",
    "VOICE_CHANNEL_PERMISSIONS",
    "GUEST_PERMISSIONS",
    "MEMBER_PERMISSIONS",
    
    # WebSocket
    "WebSocketManager",
    "websocket_manager",
    "ConnectionInfo",
    
    # Redis
    "get_redis",
    "close_redis",
    
    # Database
    "get_db_session",
    "init_db",
    "close_db",
    "engine",
    "AsyncSessionLocal",
    
    # Permissions
    "PermissionCalculator",
    "PermissionValidator",
    "RoleData",
    "PermissionOverrideData",
]