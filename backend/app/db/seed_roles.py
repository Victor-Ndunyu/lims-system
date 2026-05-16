from app.db.session import SessionLocal
from app.models.role import Role

DEFAULT_ROLES = [
    {"role_name": "public", "description": "Public user with read-only access to approved data."},
    {"role_name": "field_officer", "description": "Field officer who can create and edit pending sample submissions."},
    {"role_name": "analyst", "description": "Laboratory analyst who can add analysis results and update processing status."},
    {"role_name": "reviewer", "description": "Reviewer who can approve, reject, and publish records."},
    {"role_name": "admin", "description": "System administrator with full control over users, roles, and configuration."},
]


def seed_roles() -> None:
    with SessionLocal() as session:
        for role_data in DEFAULT_ROLES:
            existing = session.query(Role).filter_by(role_name=role_data["role_name"]).first()
            if not existing:
                session.add(Role(**role_data))
        session.commit()


if __name__ == "__main__":
    seed_roles()
