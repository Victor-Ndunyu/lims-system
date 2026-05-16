import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models import Location, Role, SampleType, User

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_data(db):
    role_names = ["field_officer", "reviewer", "admin"]
    roles = {}
    for role_name in role_names:
        role = Role(role_name=role_name, description=f"{role_name} role")
        db.add(role)
        roles[role_name] = role
    db.commit()
    for role in roles.values():
        db.refresh(role)

    users = {}
    for role_name, role in roles.items():
        user = User(
            full_name=f"{role_name} user",
            email=f"{role_name}@example.com",
            password_hash=hash_password("password"),
            role_id=role.id,
        )
        db.add(user)
        users[role_name] = user
    sample_type = SampleType(name="Water", description="Water sample")
    location = Location(country="Testland", county="Testshire", subcounty="Testville", site_name="Test Site")
    db.add_all([sample_type, location])
    db.commit()

    for item in [*users.values(), sample_type, location]:
        db.refresh(item)

    return {"roles": roles, "users": users, "sample_type": sample_type, "location": location}
