"""Database connection and session management"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from pathlib import Path
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Convert SQLite URL to async format
# sqlite:///path -> sqlite+aiosqlite:///path
DATABASE_URL = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
# Ensure database directory exists
database_path = settings.DATABASE_URL.replace("sqlite:///", "")
Path(database_path).parent.mkdir(parents=True, exist_ok=True)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for all models
Base = declarative_base()


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get a database session.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """Initialize database - create all tables"""
    logger.info("Initializing database...")
    async with engine.begin() as connection:
        # Create tables if they don't exist
        await connection.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
