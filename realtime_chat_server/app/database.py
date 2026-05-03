import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from aioredis import from_url
import asyncio

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "realtime_chat.db")

DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
REDIS_URL = "redis://localhost:6379"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)

redis_client = from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


class Base(DeclarativeBase):
    pass


async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_redis():
    return redis_client


async def close_db():
    await engine.dispose()


async def close_redis():
    await redis_client.close()
    await redis_client.aclose()
