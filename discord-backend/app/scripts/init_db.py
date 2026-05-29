import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import init_db
from app.config import settings

async def main():
    print("Initializing database...")
    await init_db()
    print(f"Database initialized at: {settings.DATABASE_URL}")

if __name__ == "__main__":
    asyncio.run(main())