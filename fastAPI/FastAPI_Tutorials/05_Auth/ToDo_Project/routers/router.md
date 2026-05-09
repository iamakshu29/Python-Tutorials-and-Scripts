# router.md -- Understanding Routers in FastAPI

## The Problem: Why Not Put Everything in main.py?

In a small app, all routes go in `main.py`. As the app grows, this becomes messy:

```
main.py
  GET  /auth
  POST /auth
  POST /token
  GET  /todos
  POST /todos
  PUT  /todos/{id}
  DELETE /todos/{id}
  ... (and many more)
```

One file handling authentication, todos, users, payments — it becomes unreadable and hard to maintain.

---

## The Solution: APIRouter

FastAPI lets you split routes across multiple files using `APIRouter`.  
Each router is like a **mini-app** with its own set of routes, and you attach them all to the main app.

---

## How It Works — Step by Step

### Step 1: Create a router in a separate file

```python
# routers/auth.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/auth")
async def get_user():
    ...

@router.post("/token")
async def login():
    ...
```

`APIRouter()` is exactly like `FastAPI()` for defining routes — just not the main app.  
`@router.get(...)` instead of `@app.get(...)`.

---

### Step 2: Include the router in main.py

```python
# main.py
from fastapi import FastAPI
from routers import auth, todos

app = FastAPI()

app.include_router(auth.router)
app.include_router(todos.router)
```

`include_router()` tells FastAPI:  
*"Take all routes defined inside this router and add them to the main app."*  
After this, `/auth`, `/token`, `/todos` etc. are all available as if they were written directly in `main.py`.

---

## Request Flow

```
Client sends: POST /token

  main.py  (app)
      |
      | -- app.include_router(auth.router) wired this up
      |
  routers/auth.py  (router)
      |
      @router.post("/token")
      |
      async def login_for_access_token(...)
```

FastAPI routes the request through the main app, which delegates to whichever router owns that path.

---

## Optional: Adding a Prefix and Tags

You can give all routes in a router a common URL prefix and a Swagger UI tag:

```python
app.include_router(auth.router,  prefix="/auth",  tags=["Authentication"])
app.include_router(todos.router, prefix="/todos", tags=["Todos"])
```

Then:
- `@router.post("/")` becomes `POST /auth/`
- `@router.get("/{id}")` becomes `GET /todos/{id}`

This avoids repeating `/auth` or `/todos` in every single route definition inside the router.

---

## Why Use Routers?

| Without Routers           | With Routers                        |
|---------------------------|-------------------------------------|
| All routes in main.py     | Routes split by feature/domain      |
| Hard to navigate          | Each file has one clear purpose     |
| Hard to split team work   | Teams can own separate router files |
| Grows into one large file | Each file stays small and focused   |

---

## File Structure in This Project

```
05_Auth/ToDo_Project/
    main.py              <- entry point; includes routers
    models.py            <- SQLAlchemy DB models
    db.py                <- engine, SessionLocal, Base
    routers/
        auth.py          <- /auth and /token routes (this router)
        todos.py         <- /todos routes (to be added)
        router.md        <- this file
        jwt_utils.py     <- educational: how JWT works internally
```
