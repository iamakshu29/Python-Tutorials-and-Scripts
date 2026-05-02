# 03_ToDo_Project/main.py -- FastAPI + SQLAlchemy: Full CRUD with a Real DB
# uvicorn main:app --reload

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path, Query, Body
from starlette import status
import models
from models import Todos
from db import engine, SessionLocal
from Todo import Todo


# =============================================
# IMPORTS EXPLAINED
# =============================================
# Annotated    - attaches metadata (like Depends) to a type hint in one clean declaration
# Session      - SQLAlchemy session type; the object used to query/write to the DB
# Depends      - FastAPI dependency injection; tells FastAPI to call get_db() and inject its result
# models       - imported to call Base.metadata.create_all (table creation on startup)
# Todos        - the SQLAlchemy class that maps to the "todos" DB table (defined in models.py)
# engine       - the DB connection created in db.py
# SessionLocal - the session factory from db.py; get_db() uses this to open sessions
# status       - Starlette named HTTP status code constants (e.g. HTTP_200_OK)
# Todo         - the Pydantic model that validates the incoming request body (defined in Todo.py)

app = FastAPI()


# =============================================
# TABLE CREATION: Auto-create DB tables on startup
# =============================================
# create_all() checks if tables defined in models.py exist in the DB.
# If they don't exist -> creates them based on the column definitions in models.py.
# If they already exist -> does nothing (safe to call every time the app starts).
models.Base.metadata.create_all(bind=engine)


# =============================================
# get_db(): DB Session per request (with cleanup)
# =============================================
# Every request needs its own DB session, and the session must be closed after.
# get_db() handles the full lifecycle using a Python generator (yield).
#
# yield splits this function into two parts:
#   BEFORE yield -> runs when the request starts (opens the session)
#   AFTER yield  -> runs when the request ends (commits or rolls back, then closes)
#
# FastAPI treats this like a context manager (the "with" block you may know):
#   with open("file.txt") as f:   <- opens file, hands it over, closes it after by itself
#       data = f.read()
#
# get_db() works the same way for DB sessions:
#   1. Opens a new session (SessionLocal())
#   2. Yields (hands) it to the route function -- route runs here
#   3. Route finished with no error -> db.commit() persists all DB changes
#   4. Route raised an exception   -> db.rollback() undoes all changes (no corrupt data)
#   5. Always (finally)            -> db.close() releases the connection back to the pool
def get_db():
    db = SessionLocal()   # open a fresh session for this request
    try:
        yield db          # hand the session to the route function; pause here until route finishes
        db.commit()       # route finished without error -> persist all DB changes
    except:
        db.rollback()     # something went wrong -> undo all staged changes
        raise             # re-raise so FastAPI can return the correct error response
    finally:
        db.close()        # always release the session regardless of success or failure


# =============================================
# DbDependency: Reusable type alias
# =============================================
# Q: Where is the "type hint" in db: DbDependency?
# A: db: DbDependency IS the type hint.
#    DbDependency expands to Annotated[Session, Depends(get_db)], so writing:
#      db: DbDependency
#    is exactly the same as writing:
#      db: Annotated[Session, Depends(get_db)]
#    The alias just makes it cleaner -- no need to repeat the full thing in every route.
#
# Annotated[Session, Depends(get_db)] tells FastAPI two things:
#   - The type of db is Session (a SQLAlchemy session object)
#   - Call get_db() and inject whatever it yields as the value for db
# =============================================
# Annotated[Session, Depends(get_db)] tells FastAPI:
#   - The type of this param is Session (a SQLAlchemy session object)
#   - Call get_db() and inject whatever it yields as the value

DbDependency = Annotated[Session, Depends(get_db)]


# =============================================
# GET /  -- Read all todos
# =============================================
# db.query(Todos) -> builds a SELECT * FROM todos query (not executed yet)
# .all()          -> executes it and returns ALL matching rows as a list of Todos objects
@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: DbDependency):
    return db.query(Todos).all()


# =============================================
# GET /todo/{todo_id}  -- Read one todo by ID
# =============================================
# .filter(Todos.id == todo_id) -> adds WHERE id = todo_id (same as SQL WHERE clause)
# .first()                     -> returns the first match and stops scanning immediately
#                                 since id is a primary key (unique), there is at most one match
#                                 more efficient than .all() -- no need to scan the full table
@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(db: DbDependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found..")


# =============================================
# POST /add_task  -- Create a new todo
# =============================================
# todo_req.dict() -> converts Pydantic object to plain dict
# **todo_req.dict() -> unpacks dict as keyword arguments into Todos() constructor
# Same pattern as Project 2: Book(**book_request.dict()) -- covered in detail there.
#
# db.add(todo_model) stages the new record -- not written to DB yet.
# The actual INSERT happens when get_db() calls db.commit() after this route returns.
@app.post("/add_task", status_code=status.HTTP_201_CREATED)
async def add_todo_task(db: DbDependency, todo_req: Todo):
    todo_model = Todos(**todo_req.dict())
    db.add(todo_model)


# =============================================
# PUT /update_task?todo_id=X  -- Replace a todo
# =============================================
# PUT = full replacement (all fields must be provided, even unchanged ones).
# todo_id is a QUERY param here (?todo_id=X), not a path param -- just showing the alternative.
# Recall from Project 1: if an arg is NOT in the URL path, FastAPI treats it as a query param.
#
# db.add(todo_model) on an already-fetched object re-stages it for commit (tracks the changes).
# status 204 NO CONTENT = success but no response body returned.
@app.put("/update_task", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_task(db: DbDependency, todo_req: Todo, todo_id: int = Query(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_model.title = todo_req.title
    todo_model.description = todo_req.description
    todo_model.priority = todo_req.priority
    todo_model.complete = todo_req.complete
    db.add(todo_model)


# =============================================
# DELETE /task/{todo_id}  -- Remove a todo
# =============================================
# .delete() is a direct bulk delete at SQL level -- skips loading the object into Python.
# Unlike the GET approach (.first() -> session.delete(obj)), this goes straight to SQL DELETE.
# Returns the number of rows deleted:
#   0 -> no record matched that id -> 404
#   1 -> found and deleted         -> 204 NO CONTENT
@app.delete("/task/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: DbDependency, todo_id: int = Path(gt=0)):
    deleted = db.query(Todos).filter(Todos.id == todo_id).delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
