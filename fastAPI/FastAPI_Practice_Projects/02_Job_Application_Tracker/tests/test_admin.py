import pytest
from .utils import override_get_db, client
from main import app
from utils.db_session import get_db
from fastapi import status

app.dependency_overrides[get_db] = override_get_db


# @router.get("/users")
def test_list_valid_user_details(auth_override):
    auth_override(
        {
            "id": 1,
            "email": "abc@gmail.com",
            "role": "Admin",
        }
    )
    response = client.get("/admin/users")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_invalid_user_details(auth_override):
    auth_override(
        {
            "id": 1,
            "email": "abc@gmail.com",
            "role": "User",
        }
    )

    response = client.get("/admin/users")

    assert response.status_code == 401
    assert response.json() == {"detail": "User Not Authorized"}


# @router.get("/applications")
def test_valid_user_to_list_all_apps(auth_override):
    auth_override(
        {
            "id": 1,
            "email": "abc@gmail.com",
            "role": "Admin",
        }
    )

    response = client.get("/admin/applications")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_invalid_user_role_to_list_all_apps(auth_override):
    auth_override(
        {
            "id": 1,
            "email": "abc@gmail.com",
            "role": "User",
        }
    )

    response = client.get("/admin/applications")

    assert response.status_code == 403
    assert response.json() == {"detail": "User Not Authorized"}


# @router.get("/stats")
def test_valid_user_to_get_status(auth_override):
    auth_override(
        {
            "id": 1,
            "email": "abc@gmail.com",
            "role": "Admin",
        }
    )

    response = client.get("/admin/stats")
    assert response.status_code == 200
    assert response.json()["total_applications"] == 0
    assert isinstance(response.json()["status"], dict)
    assert response.json()["top_companies"] == []


def test_invalid_user_to_get_status(auth_override):
    auth_override(
        {
            "id": 1,
            "email": "abc@gmail.com",
            "role": "User",
        }
    )

    response = client.get("/admin/stats")

    assert response.status_code == 403
    assert response.json() == {"detail": "User Not Authorized"}
