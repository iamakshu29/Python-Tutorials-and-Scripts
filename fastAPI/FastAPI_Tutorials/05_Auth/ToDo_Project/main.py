# 05_Auth/ToDo_Project/main.py -- Auth + Router
# uvicorn main:app --reload

from fastapi import FastAPI
import models
from db import engine
from routers import auth, todos

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

#=============
# explain 
# Adding Router
#================
app.include_router(auth.router)
app.include_router(todos.router)