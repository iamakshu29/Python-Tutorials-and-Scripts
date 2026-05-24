# 03_ToDo_Project/main.py -- FastAPI + SQLAlchemy: Full CRUD with a Real DB
# uvicorn main:app --reload

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path, Query, Body
from starlette import status
from sqlalchemy.exc import SQLAlchemyError
import models
from models import Todos
from db import engine, SessionLocal
from Todo import Todo

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


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


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: DbDependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(db: DbDependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found..")


@app.post("/add_task", status_code=status.HTTP_201_CREATED)
async def add_todo_task(db: DbDependency, todo_req: Todo):
    todo_model = Todos(**todo_req.dict())
    db.add(todo_model)


@app.put("/update_task", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_task(
    db: DbDependency, todo_req: Todo, todo_id: int = Query(gt=0)
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_model.title = todo_req.title
    todo_model.description = todo_req.description
    todo_model.priority = todo_req.priority
    todo_model.complete = todo_req.complete
    db.add(todo_model)


@app.delete("/task/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: DbDependency, todo_id: int = Path(gt=0)):
    deleted = db.query(Todos).filter(Todos.id == todo_id).delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
