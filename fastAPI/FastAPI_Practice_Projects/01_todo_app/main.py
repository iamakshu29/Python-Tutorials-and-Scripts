from fastapi import FastAPI
from DB.db import engine, Base
from Routers import auth, todo

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todo.router)