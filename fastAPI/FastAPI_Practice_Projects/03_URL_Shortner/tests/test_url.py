import pytest
from fastapi import Depends, HTTPException
from .utils import override_get_db, client
from main import app
from utils.db_session import get_db

app.dependency_overrides[get_db] = override_get_db

def test_create_short_url(db, create_user):
    payload = {
        "original_url": "https://www.example.com",
    }
    response = client.post("/url/", json=payload, auth=(create_user.username, "admin123"))

    
    assert response.status_code == 201
    assert "short_code" in response.json()
    assert "short_url" in response.json()
    assert response.json()["short_url"].startswith("http")
    assert  response.json()["original_url"] == payload["original_url"]
    assert "created_at" in response.json()
    assert "expires_at" in response.json()
