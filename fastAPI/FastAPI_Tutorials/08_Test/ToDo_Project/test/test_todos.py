# pytest test/test_todos.py --disable-warnings

from .utils import *
from fastapi import status
from main import app
from routers.todos import get_current_user, get_db
from models import Todos


# Overriding Dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "title": "Learn to code",
            "description": "Need to be backend engineer",
            "priority": 3,
            "complete": False,
            "owner": 1,
        }
    ]


def test_read_by_id(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "title": "Learn to code",
        "description": "Need to be backend engineer",
        "priority": 3,
        "complete": False,
        "owner": 1,
    }


def test_read_by_id_not_found():
    response = client.get("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found.."}


def test_create_todo(test_todo):
    request_data = {
        "title": "New Todo",
        "description": "New Todo description",
        "priority": 5,
        "complete": False,
    }

    response = client.post("/add_task", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.complete == request_data.get("complete")


def test_update_todo(test_todo):
    request_data = {
        "title": "New Title",
        "description": "Need to be backend engineer",
        "priority": 3,
        "complete": False,
    }

    response = client.put("/update_task?todo_id=1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == "New Title"


def test_update_todo_not_found(test_todo):
    request_data = {
        "title": "New Title",
        "description": "Need to be backend engineer",
        "priority": 3,
        "complete": False,
    }

    response = client.put("/update_task?todo_id=999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_delete_todo(test_todo):
    response = client.delete("/task/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()  # Use a fresh session to verify the todo was removed from the database to avoid caching value issue
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete("/task/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
