# app/utils/cache.py
from typing import Optional, Any, Callable
from functools import wraps
import json
import hashlib
from redis.asyncio import Redis
from app.core.redis_client import get_redis
import asyncio

class CacheManager:
    """Redis-based cache manager"""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._redis: Optional[Redis] = None
    
    async def _get_redis(self) -> Redis:
        if not self._redis:
            self._redis = await get_redis()
        return self._redis
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        redis = await self._get_redis()
        value = await redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        redis = await self._get_redis()
        ttl = ttl or self.default_ttl
        await redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        """Delete from cache"""
        redis = await self._get_redis()
        await redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        redis = await self._get_redis()
        return await redis.exists(key) > 0
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        redis = await self._get_redis()
        cursor = 0
        while True:
            cursor, keys = await redis.scan(cursor, match=pattern, count=100)
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        key = ":".join(key_parts)
        
        # Hash long keys
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}:{key_hash}"
        
        return key

cache_manager = CacheManager()

def cached(ttl: int = 300, key_prefix: str = "cache"):
    """Cache decorator for async functions"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager.generate_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator