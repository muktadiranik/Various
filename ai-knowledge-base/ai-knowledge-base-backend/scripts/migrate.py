"""Migration helper script using Alembic"""

import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_migration():
    """Run Alembic migration"""
    print("Running database migrations...")

    # Run Alembic upgrade
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("Database migrations completed successfully.")
        print(result.stdout)
    else:
        print("Database migrations failed.")
        print(result.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_migration()