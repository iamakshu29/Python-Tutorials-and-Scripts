import pytest
from jose import jwt
from .utils import override_get_db, client
from models.User import User
from routers.auth import bcrypt_context
from main import app
from routers.auth import SECRET_KEY, ALGORITHM, create_jwt, authenticate_user
from utils.db_session import get_db
from fastapi import HTTPException, status

app.dependency_overrides[get_db] = override_get_db


def test_register_new_user(creating_user, db):
    db.add(creating_user)
    db.commit()

    get_user = db.query(User).filter(User.id == creating_user.id).first()
    assert get_user is not None


def test_creating_token(creating_user, db):

    get_JWT = create_jwt(creating_user.id, db)

    get_payload = jwt.decode(get_JWT, SECRET_KEY, algorithms=[ALGORITHM])

    assert get_payload["sub"] == creating_user.email
    assert get_payload["id"] == str(creating_user.id)
    assert get_payload["role"] == creating_user.role


def test_authenticating_user(creating_user, db):
    payload = {
        "sub": creating_user.email,
        "id": str(creating_user.id),
        "role": creating_user.role,
    }
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    user = authenticate_user(db, token)

    assert user["email"] == creating_user.email
    assert user["id"] == str(creating_user.id)


def test_missing_claims(creating_user, db):

    payload = {"id": str(creating_user.id), "role": creating_user.role}
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)

    with pytest.raises(HTTPException):
        authenticate_user(db, token)


def test_invalid_token(creating_user, db):

    payload = {"sub": "fakeuser@gmail.com", "id": 2, "role": "Admin"}
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)

    with pytest.raises(HTTPException) as exc:
        authenticate_user(db, token)

    assert exc.value.status_code == 401


def test_jwt_error(db):
    invalid_token = "this.is.not.valid"

    with pytest.raises(HTTPException) as exc:
        authenticate_user(db, invalid_token)

    assert exc.value.status_code == 401


def test_login_valid_user():
    payload = {"username": "abc@gmail.com", "password": "admin123"}
    response = client.post(
        "/auth/login",
        data=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_user():
    payload = {"username": "abcd@gmail.com", "password": "admin123"}
    response = client.post(
        "/auth/login",
        data=payload,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Either Password or Email is Incorrect"}


def test_get_current_user_info(creating_user, auth_override):
    auth_override(
        {
            "id": str(creating_user.id),
            "email": "abc@gmail.com",
            "role": "Admin",
        }
    )
    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "abc@gmail.com"
    assert response.json()["role"] == "Admin"
    assert response.json()["is_active"] is True
