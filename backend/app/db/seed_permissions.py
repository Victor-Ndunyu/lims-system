from app.db.session import SessionLocal
from app.models.permission import Permission
from app.models.role import Role

DEFAULT_PERMISSIONS = [
    {"permission_key": "create_sample", "description": "Create sample record"},
    {"permission_key": "edit_own_record", "description": "Edit own record"},
    {"permission_key": "edit_all_records", "description": "Edit all records"},
    {"permission_key": "approve_records", "description": "Approve or reject records"},
    {"permission_key": "publish_records", "description": "Publish records to public view"},
    {"permission_key": "manage_users", "description": "Create and manage users and roles"},
    {"permission_key": "view_dashboards", "description": "Access dashboards"},
    {"permission_key": "export_data", "description": "Export data"},
    {"permission_key": "upload_attachments", "description": "Upload attachments"},
]


ROLE_DEFAULT_MAP = {
    "public": ["view_dashboards"],
    "field_officer": ["create_sample", "edit_own_record", "upload_attachments", "view_dashboards"],
    "analyst": ["edit_own_record", "edit_all_records", "view_dashboards"],
    "reviewer": ["approve_records", "publish_records", "view_dashboards"],
    "admin": ["manage_users", "export_data", "view_dashboards", "edit_all_records"],
}


def seed_permissions() -> None:
    with SessionLocal() as session:
        perms = {}
        for p in DEFAULT_PERMISSIONS:
            existing = session.query(Permission).filter(Permission.permission_key == p["permission_key"]).first()
            if not existing:
                existing = Permission(**p)
                session.add(existing)
                session.commit()
                session.refresh(existing)
            perms[existing.permission_key] = existing

        for role_name, perm_keys in ROLE_DEFAULT_MAP.items():
            role = session.query(Role).filter(Role.role_name == role_name).first()
            if not role:
                continue
            role.permissions = [perms[k] for k in perm_keys if k in perms]
        session.commit()


if __name__ == "__main__":
    seed_permissions()
