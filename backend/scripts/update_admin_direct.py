#!/usr/bin/env python3
"""Update admin password directly in the database."""

import sys
from sqlalchemy import create_engine, text

def update_admin_password_direct(database_url: str, email: str, password_hash: str):
    """Update admin user password directly in database."""
    
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # First check if user exists
        result = conn.execute(
            text("SELECT id, email FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        user_id = user[0]
        print(f"✓ Found user: {email} (ID: {user_id})")
        
        # Update password
        conn.execute(
            text("UPDATE users SET password_hash = :hash WHERE id = :id"),
            {"hash": password_hash, "id": user_id}
        )
        conn.commit()
        
        print(f"✅ Password updated successfully!")
        return True


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python update_admin_direct.py <database_url> <email> <password_hash>")
        sys.exit(1)
    
    db_url = sys.argv[1]
    email = sys.argv[2]
    hash_val = sys.argv[3]
    
    success = update_admin_password_direct(db_url, email, hash_val)
    sys.exit(0 if success else 1)
