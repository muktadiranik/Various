# tests/conftest.py
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set testing environment variable
os.environ["TESTING"] = "true"

import asyncio
import pytest
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient
import pytest_asyncio

from app.main import app
from app.core.database import get_db_session
from app.core.redis_client import get_redis
from app.models.base import Base
from app.models.user import User
from app.models.guild import Guild
from app.models.channel import Channel
from app.models.message import Message
from app.models.role import Role
from app.models.member import GuildMember
from app.core.security import create_access_token

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool
)

# Create test session factory
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for testing"""
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Mock Redis client
class MockRedis:
    def __init__(self):
        self.data = {}
        self.pubsub = MockPubSub()
    
    async def sadd(self, key: str, value: Any):
        if key not in self.data:
            self.data[key] = set()
        self.data[key].add(value)
        return 1
    
    async def srem(self, key: str, value: Any):
        if key in self.data:
            self.data[key].discard(value)
        return 1
    
    async def smembers(self, key: str):
        return self.data.get(key, set())
    
    async def scard(self, key: str):
        return len(self.data.get(key, set()))
    
    async def hset(self, key: str, field: str, value: str):
        if key not in self.data:
            self.data[key] = {}
        self.data[key][field] = value
        return 1
    
    async def hgetall(self, key: str):
        return self.data.get(key, {})
    
    async def hdel(self, key: str, field: str):
        if key in self.data and field in self.data[key]:
            del self.data[key][field]
        return 1
    
    async def expire(self, key: str, seconds: int):
        return True
    
    async def delete(self, key: str):
        if key in self.data:
            del self.data[key]
        return 1
    
    async def ping(self):
        return True
    
    async def close(self):
        pass


class MockPubSub:
    def __init__(self):
        self.subscribed_channels = set()
    
    async def subscribe(self, channel: str):
        self.subscribed_channels.add(channel)
    
    async def unsubscribe(self, channel: str):
        self.subscribed_channels.discard(channel)
    
    async def get_message(self, ignore_subscribe_messages=True, timeout=1.0):
        return None
    
    async def close(self):
        pass


async def override_get_redis():
    """Override Redis dependency for testing"""
    return MockRedis()


# Apply overrides
app.dependency_overrides[get_db_session] = override_get_db_session
app.dependency_overrides[get_redis] = override_get_redis


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database session for each test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> Dict[str, Any]:
    """Create a test user"""
    from app.core.security import hash_password
    
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("Test123!"),
        discriminator="1234",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "discriminator": user.discriminator
    }


@pytest_asyncio.fixture(scope="function")
async def test_token(test_user: Dict[str, Any]) -> str:
    """Create a test access token"""
    return create_access_token(test_user["id"])


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_token: str) -> Dict[str, str]:
    """Create authorization headers"""
    return {"Authorization": f"Bearer {test_token}"}


# Function-scoped fixture for Redis cleanup (removed session-scoped)
@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_redis():
    """Ensure Redis connections are cleaned up after each test"""
    yield
    # Small delay to allow pending tasks to complete
    await asyncio.sleep(0.1)