import pytest
from datetime import datetime, timedelta, timezone
from models.User import User
from models.URL import Url
from routers.user import bcrypt_context
from .utils import TestingSessionLocal, engine
from database import Base
from uuid import uuid4

TEST_USER_UUID = uuid4()


@pytest.fixture(autouse=True)
def reset_db():
    """Drop and recreate all tables before every test for a clean state."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

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
    db.refresh(user)
    yield user


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
    db.refresh(url)
    yield url
