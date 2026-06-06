from .utils import *
from models.URL import Url
from models.User import User
from fastapi import status
from main import app
from utils.db_session import get_db
from datetime import datetime, timezone, timedelta
from uuid import uuid4

TEST_USER_UUID = uuid4()

app.dependency_overrides[get_db] = override_get_db


# Get URL Stats by Alias
def test_get_stats(create_user, create_url):
    response = client.get(
        f"/stats/{create_url.urlCode}", auth=(create_user.username, "admin123")
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["original_url"] == create_url.original_url
    assert response.json()["short_code"] == create_url.urlCode


def test_get_stats_alias_not_found(create_user):
    response = client.get("/stats/xyz1234", auth=(create_user.username, "admin123"))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Alias not found"}


def test_get_stats_user_not_found(db, create_user, create_url):
    create_user.id = TEST_USER_UUID
    db.commit()

    response = client.get(
        f"/stats/{create_url.urlCode}", auth=(create_user.username, "admin123")
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Alias not found"}
