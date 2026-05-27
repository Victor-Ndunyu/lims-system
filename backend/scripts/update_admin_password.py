#!/usr/bin/env python3
"""Update or create a super admin user with the specified email and password.

Usage:
  python -m scripts.update_admin_password <email> <password> [database_url]

Example:
  python -m scripts.update_admin_password admin@example.com <secure-password>

With explicit database URL:
  python -m scripts.update_admin_password admin@example.com <secure-password> postgresql+psycopg://user:pass@host/db
"""

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path so imports work when run as a script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User


def update_admin_password(email: str, password: str, database_url: str | None = None) -> bool:
    """Update or create a super admin user."""
    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        return False

    if database_url:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
    else:
        from app.db.session import SessionLocal

    with SessionLocal() as session:
        admin_role = session.query(Role).filter(Role.role_name == "super_admin").first()
        if not admin_role:
            print("Error: super_admin role not found. Run seed.py first.")
            return False

        user = session.query(User).filter(User.email == email).first()
        if user:
            print(f"Updating existing user: {email}")
            user.password_hash = hash_password(password)
            user.role_id = admin_role.id
            user.is_active = True
        else:
            print(f"Creating new super admin user: {email}")
            user = User(
                full_name="Super Administrator",
                email=email,
                password_hash=hash_password(password),
                role_id=admin_role.id,
                is_active=True,
            )
            session.add(user)

        try:
            session.commit()
            session.refresh(user)
            print("Success!")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role_name}")
            print(f"   Status: {'Active' if user.is_active else 'Inactive'}")
            return True
        except Exception as exc:
            session.rollback()
            print(f"Error: {exc}")
            return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/update_admin_password.py <email> <password> [database_url]")
        print("Example: python scripts/update_admin_password.py admin@example.com <secure-password>")
        sys.exit(1)

    success = update_admin_password(
        email=sys.argv[1],
        password=sys.argv[2],
        database_url=sys.argv[3] if len(sys.argv) > 3 else None,
    )
    sys.exit(0 if success else 1)
