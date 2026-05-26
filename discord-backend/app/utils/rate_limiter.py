# app/utils/rate_limiter.py
import time
from fastapi import HTTPException
from typing import Dict, Tuple
from collections import defaultdict
import asyncio
from functools import wraps

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests: int = 100, period: int = 60):
        self.requests = requests
        self.period = period
        self._clients: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """Check if request is allowed"""
        async with self._lock:
            now = time.time()
            window_start = now - self.period
            
            # Clean old requests
            self._clients[client_id] = [
                timestamp for timestamp in self._clients[client_id]
                if timestamp > window_start
            ]
            
            # Check limit
            if len(self._clients[client_id]) >= self.requests:
                oldest = min(self._clients[client_id]) if self._clients[client_id] else now
                retry_after = int(oldest + self.period - now)
                return False, retry_after
            
            # Add current request
            self._clients[client_id].append(now)
            return True, 0
    
    async def reset(self, client_id: str):
        """Reset rate limit for client"""
        async with self._lock:
            if client_id in self._clients:
                del self._clients[client_id]

def rate_limit(requests: int = 100, period: int = 60):
    """Rate limiting decorator"""
    limiter = RateLimiter(requests, period)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract client identifier (assuming first arg is request or current_user)
            client_id = None
            for arg in args:
                if hasattr(arg, 'headers') and hasattr(arg, 'client'):
                    # FastAPI Request object
                    client_id = arg.client.host if arg.client else "unknown"
                    break
                elif isinstance(arg, dict) and 'id' in arg:
                    # User dict
                    client_id = f"user_{arg['id']}"
                    break
            
            if not client_id:
                client_id = "anonymous"
            
            allowed, retry_after = await limiter.is_allowed(client_id)
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)}
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator