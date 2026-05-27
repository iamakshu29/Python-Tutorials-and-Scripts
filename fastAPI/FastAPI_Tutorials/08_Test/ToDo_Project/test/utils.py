import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from fastapi.testclient import TestClient
from models import Todos, User
from db import Base
from main import app
from routers.users import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # new
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB commit failed: {e}")
    finally:
        db.close()


def override_get_current_user():
    return {"username": "rahul123", "user_id": 1, "user_role": "admin"}


client = TestClient(app)


# creating todos data
@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code",
        description="Need to be backend engineer",
        priority=3,
        complete=False,
        owner=1,
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


# creating a user
@pytest.fixture
def test_user():
    user = User(
        email="rahul123@gmail.com",
        username="rahul123",
        first_name="rahul",
        last_name="jain",
        hashed_password=bcrypt_context.hash("admin123"),
        role="admin",
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
