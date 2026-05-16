from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password


def seed_admin(email: str = "admin@example.com", password: str = "ChangeMe123!"):
    with SessionLocal() as session:
        role = session.query(Role).filter(Role.role_name == "admin").first()
        if not role:
            role = Role(role_name="admin", description="Administrator")
            session.add(role)
            session.commit()
            session.refresh(role)

        existing = session.query(User).filter(User.email == email).first()
        if existing:
            print("Admin already exists")
            return

        user = User(full_name="Administrator", email=email, password_hash=hash_password(password), role=role)
        session.add(user)
        session.commit()
        print("Admin user created", email)


def seed_all_admins():
    """Seed default and additional admin users."""
    admins = [
        ("admin@example.com", "ChangeMe123!"),
        ("vndunyu@gmail.com", "Animalhealth123+"),
    ]
    for email, password in admins:
        seed_admin(email, password)


if __name__ == "__main__":
    seed_all_admins()
