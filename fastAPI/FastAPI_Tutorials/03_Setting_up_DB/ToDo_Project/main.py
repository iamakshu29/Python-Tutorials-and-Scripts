# root folder for our fastAPI app
from sqlalchemy.util.typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path, Query, Body
import models
from models import Todos
from db import engine, SessionLocal
from starlette import status
from Todo import Todo

app = FastAPI()

# to create todos.db
models.Base.metadata.create_all(bind=engine)








# understand this 
# Key takeaway
# yield splits your function into setup and teardown
# FastAPI controls execution before and after yield
# It explicitly resumes the generator after your route finishes
# That’s how commit(), rollback(), and close() run

# FastAPI calling next() before your route
# FastAPI calling next() (or throw()) after your route

# Why this works
# FastAPI wraps generator dependencies similarly to a context manager (with block).
# what context manager do is if its open a file (for example), then it will close it by itself after process is complete
# with open("file.txt", "r") as f:
#     data = f.read()
# under the hood of context manager (with block)
# f = open("file.txt", "r")
# try:
#     data = f.read()
# finally:
#     f.close()

# Similarly fastAPI uses get_db function in similar way as context manager
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







# dependency injection is used 
# which means read_all function depends on get_db func to create a session and enable us to use a DB
# close the session after our requirement is done.
# Depends() in FastAPI is a powerful tool used to specify the dependencies that need to be injected for an application or function to operate correctly, 
# ensuring that all necessary components are available when they are needed.
db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/",status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all() # to get all data from our Todos DB

@app.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
# filter and return the first match...
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first() 
# first() is used to optimize our result speed as we know it is a primary key which have unique instance
# So, it doesnot search for the whole table for another instances and just return the first row that got filtered
    
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found..")





@app.post("/add_task",status_code=status.HTTP_201_CREATED)
async def add_todo_task(db: db_dependency,todo_req: Todo): # data type of Pydantic Class Todo.py
    todo_model = Todos(**todo_req.dict()) # dict is converted to keywords args for the Todos Object for DB schema  
    db.add(todo_model)  # values added and ready to commit



# as put is updating all the field again, so we have to pass all the fields with the value, either we update all field or not.db_dependency
# see the patch example in 02_project ....there we pass only the field we updated...
@app.put("/update_task",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_task(db: db_dependency,todo_req: Todo,todo_id: int = Query(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model:
        todo_model.title = todo_req.title
        todo_model.description = todo_req.description
        todo_model.priority = todo_req.priority
        todo_model.complete = todo_req.complete
        db.add(todo_model)
    else:
        raise HTTPException(status_code=404,detail="Todo not found")




@app.delete("/task/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency,todo_id: int = Path(gt=0)):
    deleted = db.query(Todos).filter(Todos.id == todo_id).delete() # gives number of affected rows

    if deleted == 0: # if 0 rows affected means not found, raise error
        raise HTTPException(status_code=404,detail="Todo not found")

        