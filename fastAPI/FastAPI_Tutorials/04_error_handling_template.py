# 04_error_handling_template.py -- FastAPI Error Handling: The 4-Layer Pattern

# =============================================
# Use of LOGGING:
# =============================================
# logging.error(...) writes the real error details to your SERVER LOGS (not to the client).
# You NEVER expose internal error details to the client -- that is a security risk.
#
#   logging.error(f"DB error: {e}")         -> goes to your server logs (for YOU to debug)
#   raise HTTPException(detail="Database error") -> goes to the client (generic, safe)
#
# Rule: log for yourself, keep client messages generic.
# import logging is a Python built-in -- no install needed.


# =============================================
# WHAT HAPPENS IF YOU DON'T HANDLE AN ERROR?
# =============================================
# If an exception escapes all your layers unhandled, FastAPI catches it automatically
# and returns HTTP 500 Internal Server Error to the client -- but with no useful detail.
# The 4-layer pattern exists so YOU control what the client sees instead of a blind 500.


# =============================================
# THE CORE IDEA: Two types of error checking
# =============================================
# There are only two ways to handle errors in a FastAPI route:
#
#   1. plain if/raise HTTPException
#      -> use when YOU can check the condition directly in Python
#      -> no waiting on anything external
#      -> example: "is this id negative?", "does the user own this?"
#
#   2. try/except -> raise HTTPException
#      -> use when your code is WAITING for a response from somewhere else
#      -> you have no control -- the DB could be down, the API could timeout
#      -> example: db.query(...), requests.get(...), open("file.txt")
#
# Simple mental trigger:
#   "Is my code waiting for a response from somewhere else?"
#   YES -> try/except
#   NO  -> plain if/raise


# =============================================
# WHAT IS AN I/O CALL?
# =============================================
# I/O = Input/Output
# Any operation where your code sends a request OUT and waits for a response back. 
# These can fail for reasons outside your code.
#
#   DB query          -> SQLAlchemy, psycopg2      (DB could be down)
#   External API call -> requests, httpx            (API could timeout)
#   File read/write   -> open(), pathlib            (file may not exist)
#   Cache             -> Redis, Memcached           (cache server could crash)
#   Message queue     -> Kafka, RabbitMQ           (queue could be down)
#   Cloud storage     -> S3, GCS                   (storage service could fail)
#
# Everything else (checking values, comparing fields, business logic) is plain if/raise.


# =============================================
# THE 4-LAYER PATTERN: Fixed flow for every route
# =============================================
# Follow this order in every route function:
#
#   Input arrives
#       |
#   [AUTOMATIC] FastAPI/Pydantic validates types & Field() constraints
#       |
#   LAYER 1: Business rule checks   ->  plain if/raise HTTPException  (400, 403)
#       |
#   LAYER 2: I/O operation          ->  try/except -> HTTPException   (500, 502)
#       |
#   LAYER 3: Post-I/O checks        ->  plain if/raise HTTPException  (404, 409)
#       |
#   LAYER 4: Return data


# =============================================
# STATUS CODE REFERENCE
# =============================================
# 400 -> Bad input you catch manually         e.g. negative id, invalid combination of fields
# 401 -> Not logged in                        e.g. missing or invalid token
# 403 -> Logged in but not allowed            e.g. wrong owner, inactive account
# 404 -> Record does not exist                e.g. db.query returned None
# 409 -> Conflict with existing data          e.g. duplicate email on signup
# 422 -> Wrong type or format                 FastAPI raises this AUTOMATICALLY (never raise it yourself)
# 500 -> Your DB or infra crashed             e.g. SQLAlchemyError, OS error
# 502 -> External API you called failed       e.g. requests.exceptions.RequestException


# =============================================
# TEMPLATE: The 4-layer pattern applied
# =============================================
# This is a generic example -- read the layer comments to understand what goes where.

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging

@app.get("/resource/{resource_id}")
def get_resource(
    db: DbDependency,
    current_user: User,
    resource_id: int = Path(gt=0)  # Path(gt=0) -> FastAPI auto-validates; no Layer 1 check needed for this
):
    # LAYER 1: Business rule checks (no I/O -- check things you already know)
    # Only needed for conditions that Path/Query/Field CANNOT express.
    # e.g. "is this user active?", "do two fields conflict?" -- these need manual if/raise.
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    # LAYER 2: I/O operation -- wrap ONLY the call that can fail at infrastructure level
    # try/except catches DB/network failures that are outside your control.
    # Log the actual error for debugging, but send a generic message to the client.
    try:
        data = db.query(Resource).filter(Resource.id == resource_id).first()
    except SQLAlchemyError as e:
        logging.error(f"DB error fetching resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    # LAYER 3: Post-I/O checks -- now check what the DB/API actually returned
    # The query ran successfully but the result might still be wrong.
    if not data:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")

    if data.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this resource")

    # LAYER 4: Return
    return data


# =============================================
# REAL EXAMPLE: GET with multiple optional filters
# =============================================
# This shows the pattern applied to a more complex route with query params.
# Notice: all the filtering logic stays INSIDE the try block --
# it is all part of the same I/O operation (one DB call = one try/except).

@app.get("/todos")
def fetch_todos(
    db: DbDependency,
    status: str | None = Query(min_length=3, default=None),
    due_date: date | None = Query(default=None),
    priority: str | None = Query(min_length=3, default=None)
):
    # LAYER 1: No extra business rule checks needed here
    # Pydantic already handles min_length on the query params automatically

    # LAYER 2: I/O -- build and execute the DB query
    # All the .filter() calls are just building the query object (no DB hit yet).
    # .all() is the actual I/O -- that is the only line that talks to the DB.
    # The whole block is wrapped in one try/except because it is one logical operation.
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

    # LAYER 3: Post-I/O -- query succeeded but returned nothing
    # NOTE: Do NOT raise 404 here for filter/list endpoints.
    # 404 = the resource/endpoint itself doesn't exist.
    # An empty result from a valid filter is a normal outcome -- return 200 with empty list [].
    # 404 in Layer 3 is only correct for single-record lookups (GET /todo/{id}).

    # LAYER 4: Return
    return data


# =============================================
# KEY RULE TO REMEMBER
# =============================================
# One try/except per I/O call.
# Everything else (business logic, result checks) is plain if/raise.
# Never put if/raise checks inside the try block -- keep layers separate.


# =============================================
# ADVANCED CONCEPTS (to explore later)
# =============================================
# These build on top of what's above -- come back and add detailed notes once you learn them:
#
# 1. @app.exception_handler(ExceptionType)
#    -> global handler that catches a specific exception type across ALL routes
#    -> avoids repeating the same try/except in every route
#
# 2. Custom exception classes
#    -> define your own exception types (e.g. class ItemNotFound(Exception))
#    -> pair with exception_handler for cleaner separation
#
# 3. RequestValidationError customisation
#    -> override FastAPI's default 422 response to change its format
#    -> useful when your frontend expects a specific error shape
