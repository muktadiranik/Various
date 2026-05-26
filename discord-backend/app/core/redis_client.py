# app/core/redis_client.py
from typing import Optional
import redis.asyncio as redis
from redis.asyncio import Redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """Get Redis client instance (singleton)"""
    global _redis_client
    if _redis_client is None:
        _redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS
        )
        logger.info("Redis client connected")
    return _redis_client


async def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed")


async def get_redis_pubsub() -> redis.client.PubSub:
    """Get Redis pubsub instance"""
    redis_client = await get_redis()
    return redis_client.pubsub()


async def check_redis_health() -> bool:
    """Check Redis health"""
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False