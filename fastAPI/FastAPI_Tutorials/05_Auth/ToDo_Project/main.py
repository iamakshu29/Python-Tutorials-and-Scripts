# 05_Auth/ToDo_Project/main.py -- Auth + Router
# uvicorn main:app --reload

# FastAPI  - the main app class
# models   - our SQLAlchemy model module; needed here to call create_all()
# engine   - the DB connection from db.py; passed to create_all() to know WHERE to create tables
# auth     - the authentication router (handles /auth and /token endpoints)
# todos    - the todos CRUD router (handles /todos endpoints)
from fastapi import FastAPI
import models
from db import engine
from routers import auth, todos, admin, users

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# =============================================
# ROUTERS
# =============================================
# As the app grows, putting ALL routes in one file (main.py) becomes unmanageable.
# FastAPI lets us split routes into separate files using APIRouter.
# Each router is like a mini-app with its own set of routes.
# include_router() attaches a router's routes to the main app.
# After this, FastAPI treats those routes exactly as if they were defined in main.py.
# See routers/router.md for the full explanation of the router pattern.
app.include_router(auth.router)   # mounts all routes defined in routers/auth.py  -> /auth/*
app.include_router(todos.router)  # mounts all routes defined in routers/todos.py -> /todos/* (protected)
app.include_router(admin.router)  # mounts all routes defined in routers/admin.py  -> /admin/* (admin only)
app.include_router(users.router)  # mounts all routes defined in routers/users.py  -> /users/* (protected)