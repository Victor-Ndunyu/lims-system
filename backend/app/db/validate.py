"""Database connection validation and health check."""

import sys

from sqlalchemy import inspect, text

from app.core.config import settings
from app.db.session import engine


def mask_database_url(database_url: str) -> str:
    scheme, separator, remainder = database_url.partition("://")
    if not separator:
        return "****"

    credentials, at, host_and_path = remainder.rpartition("@")
    if not at:
        return f"{scheme}://****"

    username = credentials.split(":", 1)[0] or "user"
    return f"{scheme}://{username}:****@{host_and_path}"


def validate_connection() -> bool:
    """Validate database connectivity and report current schema state."""
    try:
        print("Validating database connection...")
        print(f"   Database URL: {mask_database_url(settings.database_url)}")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Connected to PostgreSQL: {version.split(',')[0]}")

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\nExisting tables ({len(tables)}):")
        if tables:
            for table in sorted(tables):
                print(f"   - {table}")
        else:
            print("   No tables found - run migrations to initialize schema")

        required_tables = {
            "roles": "User roles",
            "users": "User accounts",
            "permissions": "Permissions",
            "role_permissions": "Role-permission mapping",
            "user_permissions": "User-level permission overrides",
            "sample_types": "Sample types",
            "locations": "Collection locations",
            "samples": "Sample records",
            "attachments": "Sample attachments",
            "sample_reviews": "Sample reviews",
            "audit_logs": "Audit logs",
            "sessions": "User sessions",
        }

        print("\nRequired tables status:")
        missing = []
        for table, description in required_tables.items():
            if table in tables:
                columns = inspector.get_columns(table)
                print(f"   OK      {table:20} ({len(columns)} columns) - {description}")
            else:
                print(f"   MISSING {table:20} - {description}")
                missing.append(table)

        if missing:
            print(f"\n{len(missing)} tables are missing. Run migrations:")
            print("   alembic upgrade head")
            return False

        print("\nDatabase schema is valid.")
        return True
    except Exception as exc:
        print("\nDatabase connection failed.")
        print(f"   Error: {exc}")
        print("\nCheck your DATABASE_URL in .env:")
        print("   - Ensure Supabase PostgreSQL connection is correct")
        print("   - Format: postgresql+psycopg://user:password@host:port/database")
        return False


if __name__ == "__main__":
    success = validate_connection()
    sys.exit(0 if success else 1)
