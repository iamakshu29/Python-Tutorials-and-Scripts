## The Fixed Flow
"""
Input arrives
     ↓
[FastAPI/Pydantic validates types & constraints automatically]
     ↓
Business rule checks  →  if/raise HTTPException (400, 403, 404)
     ↓
I/O operation         →  try/except → raise HTTPException (500, 502)
     ↓
Post-I/O checks       →  if/raise HTTPException (404, 409)
     ↓
Return data
"""

## The Template

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging

@app.get("/resource/{resource_id}")
def get_resource(resource_id: int, db: DbDependency, current_user: User):

    # ── LAYER 1: Business rule checks (no I/O needed) ──────────────────
    # Check things you already know without hitting the DB
    if resource_id <= 0:
        raise HTTPException(status_code=400, detail="resource_id must be positive")

    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    # ── LAYER 2: I/O operation (DB, external API, file) ────────────────
    # Wrap ONLY the call that can fail at infrastructure level
    try:
        data = db.query(Resource).filter(Resource.id == resource_id).first()
    except SQLAlchemyError as e:
        logging.error(f"DB error fetching resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    # ── LAYER 3: Post-I/O checks ────────────────────────────────────────
    # Now check what the DB/API actually returned
    if not data:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")

    if data.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this resource")

    # ── LAYER 4: Return ─────────────────────────────────────────────────
    return data


## Status Code Cheatsheet
"""

| Code | When to use | Example |
|---|---|---|
| `400` | Bad input logic you catch manually | negative ID, invalid combination |
| `401` | Not logged in | missing/invalid token |
| `403` | Logged in but not allowed | wrong owner, inactive account |
| `404` | Record doesn't exist | query returned None |
| `409` | Conflict with existing data | duplicate email on signup |
| `422` | Wrong type/format | FastAPI raises this automatically |
| `500` | Your DB/infra crashed | SQLAlchemyError, OS error |
| `502` | External API you called failed | requests.exceptions.RequestException |

"""

## Your Existing Code — Rewritten with the Template
@app.get("/todos")
def fetch_todos(
    db: DbDependency,
    status: str | None = Query(min_length=3, default=None),
    due_date: date | None = Query(default=None),
    priority: str | None = Query(min_length=3, default=None)
):
    # LAYER 1 — business rule check (optional here, Pydantic handles min_length)
    # nothing extra needed

    # LAYER 2 — I/O
    try:
        query = db.query(Todos)
        if status:
            query = query.filter(Todos.status == status)
        if due_date:
            query = query.filter(Todos.due_date == due_date)
            if not status and not priority:
                query = query.order_by(Todos.due_date.asc())
        if priority:
            query = query.filter(Todos.priority == priority)
        data = query.all()
    except SQLAlchemyError as e:
        logging.error(f"DB query failed: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    # LAYER 3 — post-I/O check
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No todos found for status={status}, due_date={due_date}, priority={priority}"
        )

    # LAYER 4 — return
    return data


# The key rule to remember: **one `try/except` per I/O call, everything else is plain `if/raise`.**
"""
I/O Calls - 
Your FastAPI app
      │
      ├── Database query        → SQLAlchemy, psycopg2
      ├── External API call     → requests, httpx
      ├── File read/write       → open(), pathlib
      ├── Cache read/write      → Redis, Memcached
      ├── Message queue         → Kafka, RabbitMQ
      └── Cloud storage         → S3, GCS
These need try/except because you have no control over them — the DB can be down, the API can timeout, the file may not exist. They can fail for reasons completely outside your code.
"""

"""
So the simple mental trigger is:

"Is my code waiting for a response from somewhere else?"

Yes → try/except
No → plain if/raise
"""