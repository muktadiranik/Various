"""Helper script to create a new Alembic migration"""

import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_migration(message: str = "auto_generated_migration"):
    """Create a new Alembic migration"""
    print(f"Creating migration: {message}...")

    # Run Alembic revision
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("Migration created successfully.")
        print(result.stdout)
    else:
        print("Migration creation failed.")
        print(result.stderr)
        sys.exit(1)


if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "auto_generated_migration"
    create_migration(message)