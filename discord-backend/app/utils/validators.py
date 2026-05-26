# app/utils/validators.py
import re
from typing import Optional

USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{2,32}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
CHANNEL_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]{2,100}$')
DISCRIMINATOR_PATTERN = re.compile(r'^\d{4}$')
INVITE_CODE_PATTERN = re.compile(r'^[A-Za-z0-9]{6,10}$')

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username:
        return False
    return bool(USERNAME_PATTERN.match(username))

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    return bool(EMAIL_PATTERN.match(email))

def validate_channel_name(name: str) -> bool:
    """Validate channel name format"""
    if not name:
        return False
    return bool(CHANNEL_NAME_PATTERN.match(name))

def validate_discriminator(discriminator: str) -> bool:
    """Validate discriminator format (4 digits)"""
    if not discriminator:
        return False
    return bool(DISCRIMINATOR_PATTERN.match(discriminator))

def validate_invite_code(code: str) -> bool:
    """Validate invite code format"""
    if not code:
        return False
    return bool(INVITE_CODE_PATTERN.match(code))

def validate_message_content(content: str, max_length: int = 2000) -> bool:
    """Validate message content"""
    if not content:
        return False
    if len(content) > max_length:
        return False
    # Check for excessive whitespace or control characters
    if any(ord(c) < 32 and c not in '\n\r\t' for c in content):
        return False
    return True

def validate_guild_name(name: str) -> bool:
    """Validate guild name"""
    if not name or len(name) < 2 or len(name) > 100:
        return False
    return True

def validate_role_name(name: str) -> bool:
    """Validate role name"""
    if not name or len(name) < 1 or len(name) > 100:
        return False
    return True

def sanitize_input(text: str, max_length: int = 1000) -> Optional[str]:
    """Sanitize user input"""
    if not text:
        return None
    
    # Trim whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove control characters except newline and tab
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    return text

def validate_permission_bitmask(bitmask: int) -> bool:
    """Validate permission bitmask"""
    from app.core.constants import Permission
    
    max_perms = 0
    for perm in Permission:
        max_perms |= perm
    
    return (bitmask & ~max_perms) == 0