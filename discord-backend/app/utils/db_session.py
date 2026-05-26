# app/utils/db_session.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session context manager"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def session_scope():
    """Decorator for session management"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with get_session() as session:
                return await func(*args, session=session, **kwargs)
        return wrapper
    return decorator

class SessionManager:
    """Session manager for manual session control"""
    def __init__(self):
        self._session: Optional[AsyncSession] = None
    
    async def __aenter__(self):
        self._session = AsyncSessionLocal()
        return self._session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            if exc_type:
                await self._session.rollback()
            else:
                await self._session.commit()
            await self._session.close()
    
    async def get_session(self) -> AsyncSession:
        if not self._session:
            self._session = AsyncSessionLocal()
        return self._session