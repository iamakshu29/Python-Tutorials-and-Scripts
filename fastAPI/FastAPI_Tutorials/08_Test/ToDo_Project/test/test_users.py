# pytest test/test_users.py --disable-warnings

from .utils import *
from fastapi import status
from main import app
from routers.todos import get_current_user, get_db
from models import User

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/users/logged_users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "rahul123@gmail.com"
    assert response.json()["username"] == "rahul123"
    assert response.json()["first_name"] == "rahul"
    assert response.json()["last_name"] == "jain"
    assert response.json()["role"] == "admin"


# we can't do simple response.json() = [ {} ] #because that will check the hashed_password as well which will change everytime because of salting, so we just check all manual fields except password


def test_update_creds_success(test_user):
    request_data = {"password": "admin123", "new_password": "admin1234"}

    response = client.put("/users/update_creds/rahul123", json=request_data)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()

    user = db.query(User).filter(User.username == "rahul123").first()

    assert user is not None

    # new password should work
    assert bcrypt_context.verify(request_data.get("new_password"), user.hashed_password)

    # old password should fail
    assert not bcrypt_context.verify("admin123", user.hashed_password)
