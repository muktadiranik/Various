# app/services/presence_service.py
from typing import Dict, List, Set, Optional
from datetime import datetime
import json
from redis.asyncio import Redis
from app.core.redis_client import get_redis
from app.core.websocket_manager import websocket_manager
from app.services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)

class PresenceService:
    def __init__(self):
        self.redis: Optional[Redis] = None
        self._initialized = False
    
    async def _ensure_redis(self):
        if not self.redis:
            self.redis = await get_redis()
            self._initialized = True
    
    async def set_user_online(self, user_id: int, guild_id: int, status: str = "online") -> None:
        await self._ensure_redis()
        
        guild_key = f"presence:guild:{guild_id}"
        await self.redis.sadd(guild_key, user_id)
        
        user_key = f"presence:user:{user_id}"
        await self.redis.hset(user_key, "status", status)
        await self.redis.hset(user_key, "last_seen", datetime.utcnow().isoformat())
        await self.redis.expire(user_key, 1800)
        
        user_guilds_key = f"presence:user:{user_id}:guilds"
        await self.redis.sadd(user_guilds_key, guild_id)
        await self.redis.expire(user_guilds_key, 1800)
        
        await redis_service.publish_user_presence(user_id, guild_id, "online")
    
    async def set_user_offline(self, user_id: int, guild_id: Optional[int] = None) -> None:
        await self._ensure_redis()
        
        if guild_id:
            guild_key = f"presence:guild:{guild_id}"
            await self.redis.srem(guild_key, user_id)
            
            user_guilds_key = f"presence:user:{user_id}:guilds"
            await self.redis.srem(user_guilds_key, guild_id)
            
            guilds_count = await self.redis.scard(user_guilds_key)
            if guilds_count == 0:
                await self.redis.delete(f"presence:user:{user_id}")
                await self.redis.delete(user_guilds_key)
            
            await redis_service.publish_user_presence(user_id, guild_id, "offline")
        else:
            user_guilds_key = f"presence:user:{user_id}:guilds"
            guilds = await self.redis.smembers(user_guilds_key)
            
            for gid in guilds:
                guild_key = f"presence:guild:{int(gid)}"
                await self.redis.srem(guild_key, user_id)
                await redis_service.publish_user_presence(user_id, int(gid), "offline")
            
            await self.redis.delete(user_guilds_key)
            await self.redis.delete(f"presence:user:{user_id}")
    
    async def get_guild_online_users(self, guild_id: int) -> Set[int]:
        await self._ensure_redis()
        guild_key = f"presence:guild:{guild_id}"
        users = await self.redis.smembers(guild_key)
        return {int(user) for user in users}
    
    async def get_user_status(self, user_id: int) -> Dict:
        await self._ensure_redis()
        user_key = f"presence:user:{user_id}"
        data = await self.redis.hgetall(user_key)
        
        if not data:
            return {"status": "offline", "last_seen": None}
        
        return {
            "status": data.get("status", "offline"),
            "last_seen": data.get("last_seen")
        }
    
    async def get_guild_online_count(self, guild_id: int) -> int:
        await self._ensure_redis()
        guild_key = f"presence:guild:{guild_id}"
        return await self.redis.scard(guild_key)
    
    async def start_typing(self, user_id: int, username: str, channel_id: int, guild_id: int) -> None:
        await self._ensure_redis()
        
        typing_key = f"typing:channel:{channel_id}"
        typing_data = {
            "user_id": user_id,
            "username": username,
            "channel_id": channel_id,
            "started_at": datetime.utcnow().isoformat()
        }
        
        await self.redis.hset(typing_key, str(user_id), json.dumps(typing_data))
        await self.redis.expire(typing_key, 10)
        
        await redis_service.publish_typing_indicator(channel_id, user_id, username, "start")
    
    async def stop_typing(self, user_id: int, channel_id: int) -> None:
        await self._ensure_redis()
        
        typing_key = f"typing:channel:{channel_id}"
        await self.redis.hdel(typing_key, str(user_id))
        
        await redis_service.publish_typing_indicator(channel_id, user_id, "", "stop")
    
    async def get_typing_users(self, channel_id: int) -> List[Dict]:
        await self._ensure_redis()
        
        typing_key = f"typing:channel:{channel_id}"
        typing_data = await self.redis.hgetall(typing_key)
        
        users = []
        for data in typing_data.values():
            users.append(json.loads(data))
        
        return users
    
    async def cleanup_stale_presence(self) -> None:
        await self._ensure_redis()
        
        pattern = "presence:user:*"
        cursor = 0
        
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            
            for key in keys:
                ttl = await self.redis.ttl(key)
                if ttl <= 0:
                    user_id = int(key.split(":")[-1])
                    await self.set_user_offline(user_id)
            
            if cursor == 0:
                break
        
        logger.info("Stale presence data cleaned up")

presence_service = PresenceService()