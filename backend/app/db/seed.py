"""Seed default roles, permissions, and the first admin user.

Required environment variables for first admin creation:
- FIRST_ADMIN_EMAIL
- FIRST_ADMIN_PASSWORD

Optional:
- FIRST_ADMIN_FULL_NAME
"""

import os
import sys

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


DEFAULT_PERMISSIONS = [
    ("create_sample_record", "Create sample records"),
    ("edit_own_record", "Edit sample records created by the user"),
    ("edit_all_records", "Edit any sample record"),
    ("approve_records", "Approve or reject submitted records"),
    ("publish_records", "Publish records to the public portal"),
    ("manage_users", "Create and manage users, roles, and permissions"),
    ("view_dashboards", "View operational dashboards"),
    ("export_data", "Export sample and analytics data"),
    ("upload_attachments", "Upload attachments to sample records"),
]


ROLE_PERMISSION_MAP = {
    "super_admin": [permission[0] for permission in DEFAULT_PERMISSIONS],
    "admin": [permission[0] for permission in DEFAULT_PERMISSIONS],
    "reviewer": ["approve_records", "publish_records", "view_dashboards", "export_data"],
    "analyst": ["edit_own_record", "edit_all_records", "view_dashboards", "export_data"],
    "field_officer": ["create_sample_record", "edit_own_record", "upload_attachments", "view_dashboards"],
    "data_entry_user": ["create_sample_record", "edit_own_record", "upload_attachments"],
    "public_viewer": [],
}


ROLE_DESCRIPTIONS = {
    "super_admin": "Full platform owner with all permissions.",
    "admin": "Administrator for user, sample, and dashboard operations.",
    "reviewer": "Scientific reviewer who approves, rejects, and publishes records.",
    "analyst": "Analyst with access to records, dashboards, and exports.",
    "field_officer": "Field officer who creates and manages own sample submissions.",
    "data_entry_user": "Data entry user for sample submission workflows.",
    "public_viewer": "Read-only public viewer role.",
}


def require_first_admin_env() -> tuple[str, str, str]:
    email = os.getenv("FIRST_ADMIN_EMAIL")
    password = os.getenv("FIRST_ADMIN_PASSWORD")
    full_name = os.getenv("FIRST_ADMIN_FULL_NAME", "System Administrator")

    if not email or not password:
        raise RuntimeError("FIRST_ADMIN_EMAIL and FIRST_ADMIN_PASSWORD must be set to seed the first admin user.")
    if len(password) < 12:
        raise RuntimeError("FIRST_ADMIN_PASSWORD must be at least 12 characters.")

    return full_name, email, password


def seed_database() -> bool:
    try:
        full_name, admin_email, admin_password = require_first_admin_env()
        with SessionLocal() as session:
            permissions = {}
            for permission_key, description in DEFAULT_PERMISSIONS:
                permission = session.query(Permission).filter(Permission.permission_key == permission_key).first()
                if not permission:
                    permission = Permission(permission_key=permission_key, description=description)
                    session.add(permission)
                    session.flush()
                permissions[permission_key] = permission

            roles = {}
            for role_name, permission_keys in ROLE_PERMISSION_MAP.items():
                role = session.query(Role).filter(Role.role_name == role_name).first()
                if not role:
                    role = Role(role_name=role_name, description=ROLE_DESCRIPTIONS[role_name])
                    session.add(role)
                    session.flush()
                role.permissions = [permissions[key] for key in permission_keys]
                roles[role_name] = role

            admin_user = session.query(User).filter(User.email == admin_email).first()
            if not admin_user:
                admin_user = User(
                    full_name=full_name,
                    email=admin_email,
                    password_hash=hash_password(admin_password),
                    role=roles["super_admin"],
                    is_active=True,
                )
                session.add(admin_user)

            session.commit()
            print("Database seed completed.")
            print(f"First admin user: {admin_email}")
            return True
    except Exception as exc:
        print(f"Database seed failed: {exc}")
        return False


if __name__ == "__main__":
    sys.exit(0 if seed_database() else 1)
