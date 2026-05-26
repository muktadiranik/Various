# app/utils/helpers.py
import random
import string
from datetime import datetime
from typing import Optional

def generate_discriminator() -> str:
    """Generate random 4-digit discriminator"""
    return str(random.randint(1000, 9999))

def generate_invite_code(length: int = 8) -> str:
    """Generate random invite code"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def format_timestamp(dt: datetime, format: str = "iso") -> str:
    """Format timestamp"""
    if format == "iso":
        return dt.isoformat()
    elif format == "unix":
        return str(int(dt.timestamp()))
    elif format == "readable":
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.isoformat()

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse timestamp string to datetime"""
    try:
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError):
        try:
            return datetime.fromtimestamp(int(timestamp_str))
        except (ValueError, TypeError):
            return None

def chunk_list(lst: list, chunk_size: int):
    """Split list into chunks"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Merge two dictionaries recursively"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def remove_none_values(data: dict) -> dict:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}

def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.utcnow()

def class_to_dict(obj) -> dict:
    """Convert class instance to dictionary"""
    if hasattr(obj, '__dict__'):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return {}

def safe_int_convert(value, default: int = 0) -> int:
    """Safely convert to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float_convert(value, default: float = 0.0) -> float:
    """Safely convert to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default