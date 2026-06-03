import pytest
from uuid import uuid4
from models.User import User
from models.Application import Application
from routers.auth import bcrypt_context, authenticate_user
from .utils import TestingSessionLocal
from main import app
from datetime import datetime, timezone, date

TEST_USER_UUID = uuid4()


@pytest.fixture
def creating_user():
    user = User(
        id=TEST_USER_UUID,
        email="abc@gmail.com",
        hashed_password=bcrypt_context.hash("admin123"),
        role="Admin",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    return user


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_override():
    def _set(user):
        app.dependency_overrides[authenticate_user] = lambda: user

    yield _set
    if authenticate_user in app.dependency_overrides:
        del app.dependency_overrides[authenticate_user]


@pytest.fixture
def creating_app():
    app = Application(
        id=uuid4(),
        user_id=TEST_USER_UUID,
        company="XYZ",
        role_title="Developer",
        status="Applied",
    )
    return app
