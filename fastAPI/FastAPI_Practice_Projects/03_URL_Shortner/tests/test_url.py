import pytest
from fastapi import status
from .utils import override_get_db, client
from main import app
from models.User import User, UserSubscription
from models.URL import Url
from utils.db_session import get_db
from uuid import UUID
from .conftest import TEST_USER_UUID
from datetime import datetime, timezone, timedelta

app.dependency_overrides[get_db] = override_get_db


# Create Short_url
def test_create_short_url_valid_user(create_user):
    payload = {
        "original_url": "https://www.example.com/",
    }
    response = client.post(
        "/url/", json=payload, auth=(create_user.username, "admin123")
    )

    assert response.status_code == 201
    assert "short_code" in response.json()
    assert "short_url" in response.json()
    assert response.json()["short_url"].startswith("http")
    assert response.json()["original_url"] == payload["original_url"]
    assert "created_at" in response.json()
    assert "expires_at" in response.json()


def test_create_short_url_invalid_user(create_user):
    payload = {
        "original_url": "https://www.example.com/",
    }
    response = client.post("/url/", json=payload, auth=("testUser", "admin123"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_short_url_admin_user(db, create_user):
    payload = {
        "original_url": "https://www.example.com/",
    }
    data = db.query(User).filter(User.username == "abc").first()
    data.role = "Admin"
    db.commit()
    response = client.post(
        "/url/", json=payload, auth=(create_user.username, "admin123")
    )

    assert data.role == "Admin"
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_short_url_same_urlCode(db, create_user, create_url):
    payload = {"original_url": create_url.original_url, "urlCode": create_url.urlCode}

    response = client.post(
        "/url/", json=payload, auth=(create_user.username, "admin123")
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Unable to add URL"}


# Get All Url created by the authenticated user.
def test_get_all_urls_valid_user(create_user, create_url):
    response = client.get("/url/", auth=(create_user.username, "admin123"))

    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["original_url"] == "https://www.example.com/"
    assert UUID(response.json()[0]["user_id"]) == TEST_USER_UUID


def test_get_all_urls_invalid_user():
    response = client.get("/url/", auth=("testUser", "admin123"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not Validate User"}


# Get Url by Alias/Short Code of logged in username
def test_get_url_by_alias_valid_user(create_url, create_user):
    response = client.get(
        f"/url/{create_url.urlCode}", auth=(create_user.username, "admin123")
    )

    assert response.json()["original_url"] == "https://www.example.com/"
    assert response.json()["urlCode"] == create_url.urlCode


def test_get_url_by_alias_invalid_user():
    response = client.get("/url/abc1234", auth=("testUser", "admin123"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not Validate User"}


def test_get_url_by_alias_not_matched(create_user):
    response = client.get("/url/xyz1234", auth=(create_user.username, "admin123"))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Alias Not Found"}


# Upgrade/renew an expired URL.
def test_upgrade_expired_url_basic_user(create_user):
    response = client.patch(
        "/url/upgrade/abc1234", auth=(create_user.username, "admin123")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Basic User can't upgrade the URL, Upgrade Membership to Update Expiry_date and Alias"
    }


# $ check the test, also understand hy we need to time timezones
def test_upgrade_expired_url_premium_user_url_expired(db, create_url, create_user):
    create_user.subscription_type = UserSubscription.premium

    create_url.expires_at = datetime.now(timezone.utc) - timedelta(minutes=10)
    db.commit()

    response = client.patch(
        "/url/upgrade/abc1234", auth=(create_user.username, "admin123")
    )

    assert (
        response.json()["status"]
        == "Alias and Expiry Time has now been updated as part of your Premier Membership"
    )


def test_upgrade_expired_url_premium_user_url_not_expired(db, create_url, create_user):
    create_user.subscription_type = UserSubscription.premium
    db.commit()

    response = client.patch(
        "/url/upgrade/abc1234", auth=(create_user.username, "admin123")
    )

    assert response.json()["status"] == "URL Not expired Yet"
