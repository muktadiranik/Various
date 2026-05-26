# app/core/constants.py
from enum import IntFlag
from typing import Optional


class Permission(IntFlag):
    """Bitmask permissions for Discord-like system"""
    
    # Channel permissions (0x00000001 - 0x00001000)
    VIEW_CHANNEL = 1 << 0          # 0x00000001
    SEND_MESSAGES = 1 << 1         # 0x00000002
    READ_MESSAGE_HISTORY = 1 << 2  # 0x00000004
    CREATE_INVITE = 1 << 3         # 0x00000008
    MANAGE_MESSAGES = 1 << 4       # 0x00000010
    ADD_REACTIONS = 1 << 5         # 0x00000020
    ATTACH_FILES = 1 << 6          # 0x00000040
    EMBED_LINKS = 1 << 7           # 0x00000080
    MENTION_EVERYONE = 1 << 8      # 0x00000100
    USE_EXTERNAL_EMOJIS = 1 << 9   # 0x00000200
    CONNECT = 1 << 10              # 0x00000400 (Voice)
    SPEAK = 1 << 11                # 0x00000800 (Voice)
    MUTE_MEMBERS = 1 << 12         # 0x00001000 (Voice)
    DEAFEN_MEMBERS = 1 << 13       # 0x00002000 (Voice)
    MOVE_MEMBERS = 1 << 14         # 0x00004000 (Voice)
    USE_VAD = 1 << 15              # 0x00008000 (Voice)
    
    # Guild permissions (0x00010000 - 0x10000000)
    MANAGE_CHANNELS = 1 << 16      # 0x00010000
    MANAGE_GUILD = 1 << 17         # 0x00020000
    ADMINISTRATOR = 1 << 18        # 0x00040000
    MANAGE_ROLES = 1 << 19         # 0x00080000
    MANAGE_NICKNAMES = 1 << 20     # 0x00100000
    CHANGE_NICKNAME = 1 << 21      # 0x00200000
    KICK_MEMBERS = 1 << 22         # 0x00400000
    BAN_MEMBERS = 1 << 23          # 0x00800000
    VIEW_AUDIT_LOG = 1 << 24       # 0x01000000
    MANAGE_WEBHOOKS = 1 << 25      # 0x02000000
    MANAGE_EMOJIS = 1 << 26        # 0x04000000
    
    @classmethod
    def all_permissions(cls) -> int:
        """Get all permissions combined"""
        all_perms = 0
        for perm in cls:
            all_perms |= perm
        return all_perms
    
    @classmethod
    def from_string(cls, permission_name: str) -> Optional['Permission']:
        """Get permission from string name"""
        try:
            return cls[permission_name.upper()]
        except KeyError:
            return None


# Default role permissions
DEFAULT_EVERYONE_PERMISSIONS = (
    Permission.VIEW_CHANNEL |
    Permission.SEND_MESSAGES |
    Permission.READ_MESSAGE_HISTORY |
    Permission.ADD_REACTIONS |
    Permission.ATTACH_FILES |
    Permission.EMBED_LINKS |
    Permission.CONNECT |
    Permission.SPEAK |
    Permission.CHANGE_NICKNAME |
    Permission.USE_VAD
)

DEFAULT_ADMIN_PERMISSIONS = Permission.ADMINISTRATOR

DEFAULT_MODERATOR_PERMISSIONS = (
    Permission.MANAGE_MESSAGES |
    Permission.KICK_MEMBERS |
    Permission.BAN_MEMBERS |
    Permission.MANAGE_NICKNAMES |
    Permission.VIEW_AUDIT_LOG |
    Permission.MUTE_MEMBERS |
    Permission.MOVE_MEMBERS |
    Permission.DEAFEN_MEMBERS
)

# Role position defaults
ADMIN_ROLE_POSITION = 100
MODERATOR_ROLE_POSITION = 50
DEFAULT_ROLE_POSITION = 0

# Channel type specific permissions
TEXT_CHANNEL_PERMISSIONS = (
    Permission.VIEW_CHANNEL |
    Permission.SEND_MESSAGES |
    Permission.READ_MESSAGE_HISTORY |
    Permission.MANAGE_MESSAGES |
    Permission.ADD_REACTIONS |
    Permission.ATTACH_FILES |
    Permission.EMBED_LINKS |
    Permission.MENTION_EVERYONE |
    Permission.USE_EXTERNAL_EMOJIS
)

VOICE_CHANNEL_PERMISSIONS = (
    Permission.VIEW_CHANNEL |
    Permission.CONNECT |
    Permission.SPEAK |
    Permission.MUTE_MEMBERS |
    Permission.MOVE_MEMBERS |
    Permission.DEAFEN_MEMBERS |
    Permission.USE_VAD
)

# Guest/user permissions
GUEST_PERMISSIONS = (
    Permission.VIEW_CHANNEL |
    Permission.READ_MESSAGE_HISTORY
)

MEMBER_PERMISSIONS = GUEST_PERMISSIONS | (
    Permission.SEND_MESSAGES |
    Permission.ADD_REACTIONS |
    Permission.ATTACH_FILES |
    Permission.EMBED_LINKS |
    Permission.CONNECT |
    Permission.SPEAK
)