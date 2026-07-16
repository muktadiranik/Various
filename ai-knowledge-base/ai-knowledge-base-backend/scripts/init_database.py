"""Database initialization and migration helper script"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import init_database, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize the database"""
    logger.info(f"Initializing database at: {settings.DATABASE_URL}")

    try:
        await init_database()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        await engine.dispose()
        logger.info("Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
