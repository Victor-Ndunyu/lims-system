#!/usr/bin/env python3
"""Check user and role setup."""

import sys
from sqlalchemy import create_engine, text

def check_user_setup(database_url: str, email: str):
    """Check user and role setup."""
    
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Check user
        result = conn.execute(
            text("""
                SELECT u.id, u.email, u.full_name, u.is_active, u.role_id, r.role_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.email = :email
            """),
            {"email": email}
        )
        user = result.fetchone()
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        user_id, user_email, full_name, is_active, role_id, role_name = user
        print(f"✓ User Found:")
        print(f"  ID: {user_id}")
        print(f"  Email: {user_email}")
        print(f"  Name: {full_name}")
        print(f"  Active: {is_active}")
        print(f"  Role ID: {role_id}")
        print(f"  Role Name: {role_name}")
        
        if not role_id:
            print(f"\n❌ ERROR: User has no role assigned!")
            return False
        
        if not role_name:
            print(f"\n❌ ERROR: Role not found! Role ID {role_id} doesn't exist in roles table")
            return False
        
        # Check role permissions
        result = conn.execute(
            text("""
                SELECT p.permission_key
                FROM role_permissions rp
                JOIN permissions p ON rp.permission_id = p.id
                WHERE rp.role_id = :role_id
            """),
            {"role_id": role_id}
        )
        permissions = [row[0] for row in result.fetchall()]
        print(f"\n✓ Permissions ({len(permissions)}):")
        for perm in permissions:
            print(f"  - {perm}")
        
        return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python check_user.py <database_url> <email>")
        sys.exit(1)
    
    db_url = sys.argv[1]
    email = sys.argv[2]
    
    success = check_user_setup(db_url, email)
    sys.exit(0 if success else 1)
