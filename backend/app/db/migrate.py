"""Run database migrations safely."""
import sys
from alembic import command
from alembic.config import Config
from pathlib import Path


def run_migrations(revision="head"):
    """Apply database migrations up to specified revision."""
    try:
        config = Config("alembic.ini")
        print(f"🔄 Running migrations to {revision}...")
        command.upgrade(config, revision)
        print(f"✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False


def create_migration(message: str):
    """Generate a new migration."""
    try:
        config = Config("alembic.ini")
        print(f"✍️  Creating migration: {message}")
        command.revision(config, autogenerate=True, message=message)
        print("✅ Migration created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create migration: {str(e)}")
        return False


def downgrade_migrations(revision="-1"):
    """Downgrade migrations (use with caution)."""
    try:
        config = Config("alembic.ini")
        print(f"⚠️  Downgrading migrations to {revision}...")
        command.downgrade(config, revision)
        print("✅ Downgrade completed!")
        return True
    except Exception as e:
        print(f"❌ Downgrade failed: {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.db.migrate [upgrade|downgrade|create] [revision|message]")
        sys.exit(1)
    
    command = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command == "upgrade":
        success = run_migrations(arg or "head")
    elif command == "downgrade":
        success = run_migrations(arg or "-1")
    elif command == "create":
        success = create_migration(arg or "auto-generated")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
