import pytest
from .utils import *
from fastapi import status
from main import app
from routers.todos import get_db
from routers.auth import (
    authenticate_user,
    create_JWT,
    SECRET_KEY,
    ALGORITHM,
    get_current_user,
)
from jose import jwt
from fastapi import HTTPException
from datetime import timedelta

app.dependency_overrides[get_db] = override_get_db


# testing method authenticate_user from auth.py
def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user.username, "admin123", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_authenticated_user = authenticate_user("incorrect_username", "admin123", db)
    assert non_authenticated_user is False


def test_create_jwt(test_user):

    get_JWT = create_JWT(test_user.username, 1, test_user.role, timedelta(minutes=20))

    decode_token = jwt.decode(get_JWT, SECRET_KEY, algorithms=[ALGORITHM])

    assert decode_token.get("sub") == test_user.username
    assert decode_token.get("id") == 1
    assert decode_token.get("role") == test_user.role


# marker is required here for async app
@pytest.mark.asyncio
async def test_get_current_user(test_user):
    payload = {"sub": test_user.username, "id": 1, "role": test_user.role}
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)

    user = await get_current_user(token)

    assert user == {
        "username": test_user.username,
        "user_id": 1,
        "user_role": test_user.role,
    }


# If payload elements are missing
@pytest.mark.asyncio
async def test_get_current_user_missing_payload(test_user):
    payload = {"role": test_user.role}
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)

    with pytest.raises(HTTPException) as e:
        await get_current_user(token)

    assert e.value.status_code == 401
    assert e.value.detail == "Could not Validate User"
