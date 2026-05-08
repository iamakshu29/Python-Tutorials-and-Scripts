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

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: DbDependency):
    try:
        get_data = db.query(Todos).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    return get_data

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(db: DbDependency, todo_id: int = Path(gt=0)):
    try:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found..")

@router.post("/add_task", status_code=status.HTTP_201_CREATED)
async def add_todo_task(db: DbDependency, todo_req: Todo):
    todo_model = Todos(**todo_req.dict())
    db.add(todo_model)

@router.put("/update_task", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_task(db: DbDependency, todo_req: Todo, todo_id: int = Query(gt=0)):
    try:    
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
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
async def delete_todo(db: DbDependency, todo_id: int = Path(gt=0)):
    try:
        deleted = db.query(Todos).filter(Todos.id == todo_id).delete()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
