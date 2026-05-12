# 05_Auth/ToDo_Project/main.py -- Auth + Router
# uvicorn main:app --reload

from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from starlette import status
from models import Todos
from db import SessionLocal
from Todo import Todo
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
user_dependency = Annotated[dict,Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,db: DbDependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        get_data = db.query(Todos).filter(user.get("user_id") == Todos.owner).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    return get_data

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(user: user_dependency,db: DbDependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        todo_model = db.query(Todos).filter(Todos.owner == user.get("user_id"),Todos.id == todo_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found..")

@router.post("/add_task", status_code=status.HTTP_201_CREATED)
async def add_todo_task(user: user_dependency, db: DbDependency, todo_req: Todo):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = Todos(**todo_req.dict(), owner=user.get("user_id"))
    db.add(todo_model)

@router.put("/update_task", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_task(user: user_dependency, db: DbDependency, todo_req: Todo, todo_id: int = Query(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:    
        todo_model = db.query(Todos).filter(Todos.owner == user.get("user_id"), Todos.id == todo_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_model.title = todo_req.title
    todo_model.description = todo_req.description
    todo_model.priority = todo_req.priority
    todo_model.complete = todo_req.complete

    db.add(todo_model)

@router.delete("/task/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: DbDependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        deleted = db.query(Todos).filter(Todos.owner == user.get("user_id"), Todos.id == todo_id).delete()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
