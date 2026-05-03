from functools import wraps
from typing import Callable, Any, Optional
import json
from aioredis import Redis
from app.database import get_redis


def cache(ttl: int = 300, key_prefix: str = "cache:"):
    """Redis TTL cache decorator for async functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            redis = await get_redis()
            # Simple key from func name + args (improve for prod)
            key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            await redis.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator


class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 300):
        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str):
        await self.redis.delete(key)
