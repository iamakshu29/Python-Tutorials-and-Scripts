import pytest
from datetime import datetime, timedelta, timezone
from models.User import User
from models.URL import Url
from routers.user import bcrypt_context
from .utils import TestingSessionLocal
from uuid import uuid4

TEST_USER_UUID = uuid4()


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def create_user(db):
    user = User(
        id=TEST_USER_UUID,
        email="abc@example.com",
        username="abc",
        hashed_password=bcrypt_context.hash("admin123"),
        role="User",
        subscription_type="Basic",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture
def create_url(db):
    url = Url(
        original_url="https://www.example.com/",
        urlCode="abc1234",
        click_count=0,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=7),
        last_accessed_at=datetime.now(timezone.utc),
        user_id=TEST_USER_UUID,
    )
    db.add(url)
    db.commit()
    yield url
    db.delete(url)
    db.commit()
