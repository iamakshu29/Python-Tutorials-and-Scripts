from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from fastapi import FastAPI, Path, Query, Body, HTTPException, Depends
from datetime import date
from schemas import TodoCreate
from DB.models import Todos
from datetime import datetime
from DB.db import engine, SessionLocal, Base

app = FastAPI()
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()   
    try:
        yield db          
        db.commit()       
    except:
        db.rollback()     
        raise            
    finally:
        db.close()
DbDependency = Annotated[Session, Depends(get_db)]

# Fetch all Todos or Filter it by status, due_date, priority
@app.get("/todos",status_code=status.HTTP_200_OK)
def fetch_todos(
        db: DbDependency,
        status: str | None = Query(min_length= 3,default=None),
        due_date: date | None = Query(default=None),
        priority: str | None = Query(min_length= 3,default=None)
    ):
    try:    
        query = db.query(Todos)  # base query

        if status:
            query = query.filter(Todos.status == status)
        if due_date:
            query = query.filter(Todos.due_date == due_date)

            # if only date is asked then sort by date
            if not status and not priority:
                query = query.order_by(Todos.due_date.asc())

        if priority:
            query = query.filter(Todos.priority == priority)

        data = query.all()
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")

    if not data:
        raise HTTPException(status_code=404, detail=f"No todos found for status={status}, due_date={due_date}, priority={priority}")

    return data

# Fetch by id
@app.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
def fetch_a_todo(db: DbDependency,todo_id: int = Path(gt = 0)):
    try:
        db_data = db.query(Todos).filter(Todos.id == todo_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")

    if not db_data:
        raise HTTPException(status_code = 404, detail=f"id: {todo_id} not found")
    return db_data

# Create a task
@app.post("/todos",status_code=status.HTTP_201_CREATED)
def create_todo(db: DbDependency,todo_data: TodoCreate):
    try:
        task = Todos(**todo_data.dict())
        db.add(task)
        print(f"Task Added by User ID - {task.user_id} at {datetime.utcnow()}") # this logic in print statement work for now, but not work later as DB will create user_id automatically when user logs in
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")

    return "List created successfully"

# Update the fields
@app.put("/todos/{todo_id}",status_code=status.HTTP_202_ACCEPTED)
def update_a_todo(db: DbDependency,todo_data: TodoCreate,todo_id: int = Path(gt = 0)):
    try:
        db_data = db.query(Todos).filter(Todos.id == todo_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")

    if not db_data:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    
    db_data.title = todo_data.title
    db_data.description = todo_data.description
    db_data.status = todo_data.status
    db_data.priority = todo_data.priority
    db_data.updated_at = datetime.utcnow()
    print(f"Task Updated by User ID - {db_data.user_id} at {datetime.utcnow()}") # works here as the item is already present so user_id exists
    return "Todo updated successfully"

# Update status as Completed
@app.patch("/todos/{todo_id}/complete",status_code=status.HTTP_202_ACCEPTED)
def marks_as_complete(db: DbDependency,todo_id: int = Path(gt = 0)):
    try:
        db_data = db.query(Todos).filter(Todos.id == todo_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")

    if not db_data:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")

    if db_data.status == "Completed":
        print(f"Task Already marked as Completed") # works here as the item is already present so user_id exists
        return "Status Already Completed"

    db_data.status = "Completed"
    db_data.updated_at = datetime.utcnow()
    print(f"Marked as Completed by User ID - {db_data.user_id} at {datetime.utcnow()}") # works here as the item is already present so user_id exists
    return "Task Completed"

# Delete a Task
@app.delete("/todos/{todo_id}",status_code=status.HTTP_202_ACCEPTED)
def delete_a_todo(db: DbDependency,todo_id: int = Path(gt = 0)):
    try:
        db_data = db.query(Todos).filter(Todos.id == todo_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
        
    if not db_data:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    db_data.deleted_at = datetime.utcnow()
    print(f"Task Deleted by User ID - {db_data.user_id} at {datetime.utcnow()}") # works here as the item is already present so user_id exists
    return "Data Deleted Successfully"
        
