# pytest test/test_admin.py --disable-warnings

from .utils import *
from fastapi import status
from main import app
from routers.todos import get_current_user, get_db

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/")
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


def test_delete_todo_by_id_authenticated(test_todo):
    response = client.delete("/admin/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete("/admin/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
