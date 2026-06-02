import pytest
from .utils import override_get_db, client
from models.Application import Application
from main import app
from utils.db_session import get_db
from fastapi import HTTPException, status

app.dependency_overrides[get_db] = override_get_db


# @router.post("/")
def test_create_job_app_valid_success(db, creating_app, auth_override):
    auth_override(
        {
            "id": 1,
            "email": "abc@gmail.com",
            "role": "Admin",
        }
    )

    payload = {"company": "XYZ", "role_title": "Developer", "status": "Applied"}

    response = client.post("/app", json=payload)

    assert response.status_code == 201
    assert response.json() == {"message": "Application Posted"}


def test_create_job_app_unauthorized(db, creating_app, auth_override):
    auth_override(None)
    payload = {"company": "XYZ", "role_title": "Developer", "status": "Applied"}

    response = client.post("/app", json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication Failed"}


# @router.post("/bulk_add")
