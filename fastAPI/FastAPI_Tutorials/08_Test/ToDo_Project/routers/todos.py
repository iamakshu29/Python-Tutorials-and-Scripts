# routers/todos.py -- Todos CRUD router (authentication-protected)
# All routes here require a valid JWT token.
# The logged-in user can only see and modify THEIR OWN todos (filtered by owner = user_id).
# See admin.py for routes that bypass owner filtering (admin sees all todos).

# Annotated  - combines a type hint with metadata (Depends) in one declaration
# Session    - SQLAlchemy session type
# SQLAlchemyError - catches DB-level failures
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# APIRouter  - creates a mini-app with its own routes
# Depends    - dependency injection
# HTTPException - raises HTTP errors
# Path, Query - validate path and query parameters
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from starlette import status

# Todos - the SQLAlchemy model (DB table)
from models import Todos
from db import SessionLocal

# Todo - the Pydantic model (validates incoming request body)
from Todo import Todo

# get_current_user - the JWT validation dependency from auth.py
# it decodes the token, validates it, and returns {"username":..., "user_id":..., "user_role":...}
# any route that depends on this will automatically require a valid Bearer token in the request
from .auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB commit failed: {e}")
    finally:
        db.close()

DbDependency = Annotated[Session, Depends(get_db)]

# user_dependency -> injects the result of get_current_user into any route that declares it
# JWT decode and return dict type payload.
# get_current_user reads and validates the JWT from the Authorization header
# if the token is missing/invalid/expired -> 401 is raised automatically before the route runs
user_dependency = Annotated[dict, Depends(get_current_user)]


# =============================================
# GET / -> return all todos belonging to the logged-in user
# =============================================
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: DbDependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        # filter by owner == user_id so each user only sees THEIR todos
        # without this filter, every user would see every todo in the DB
        get_data = db.query(Todos).filter(user.get("user_id") == Todos.owner).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    return get_data


# =============================================
# GET /todo/{todo_id} -> return one todo by id (must belong to the logged-in user)
# =============================================
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(user: user_dependency, db: DbDependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        # filter by BOTH owner AND id — prevents user A from reading user B's todo by guessing an id
        todo_model = db.query(Todos).filter(Todos.owner == user.get("user_id"), Todos.id == todo_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found..")


# =============================================
# POST /add_task -> create a new todo for the logged-in user
# =============================================
@router.post("/add_task", status_code=status.HTTP_201_CREATED)
async def add_todo_task(user: user_dependency, db: DbDependency, todo_req: Todo):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # owner=user.get("user_id") automatically sets the owner to the logged-in user's id
    # the client does NOT send the owner field — it's derived from the JWT token
    # this prevents a user from creating todos owned by another user
    todo_model = Todos(**todo_req.dict(), owner=user.get("user_id"))
    db.add(todo_model)  # staged; committed in get_db() after route completes


# =============================================
# PUT /update_task?todo_id=X -> fully update a todo (must belong to the logged-in user)
# =============================================
@router.put("/update_task", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_task(user: user_dependency, db: DbDependency, todo_req: Todo, todo_id: int = Query(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        # filter by owner AND id -> user can only update their own todos
        todo_model = db.query(Todos).filter(Todos.owner == user.get("user_id"), Todos.id == todo_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # overwrite all fields (PUT = full replacement)
    todo_model.title = todo_req.title
    todo_model.description = todo_req.description
    todo_model.priority = todo_req.priority
    todo_model.complete = todo_req.complete

    db.add(todo_model)  # re-stage the modified record; committed in get_db()


# =============================================
# DELETE /task/{todo_id} -> delete a todo (must belong to the logged-in user)
# =============================================
@router.delete("/task/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: DbDependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        # filter by owner AND id -> user can only delete their own todos
        deleted = db.query(Todos).filter(Todos.owner == user.get("user_id"), Todos.id == todo_id).delete()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    if deleted == 0:  # 0 rows affected means no matching todo was found
        raise HTTPException(status_code=404, detail="Todo not found")
