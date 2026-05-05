# Todo.py -- Pydantic Request Model: Incoming request body validation

# =============================================
# PYDANTIC MODEL: Todo (same concept as Project 2)
# =============================================
# Same Pydantic pattern from Project 2 -- covered in detail in 02_books_project/books.py.
# Quick recap:
#   - FastAPI reads this class and validates the request body BEFORE the route runs
#   - If any field fails validation -> FastAPI auto-returns HTTP 422 Unprocessable Entity
#   - This model defines WHAT the client must send, not what gets stored in the DB

# Note: The field names and types here match the DB model (models.py) but they serve different purposes:
#   Todo (Pydantic) -> validates incoming request body (what the client sends)
#   Todos (SQLAlchemy) -> defines the DB table schema (what gets stored)
# Why no id field here? Because id is auto-assigned by the DB on INSERT (defined in models.py as primary_key).
from pydantic import BaseModel, Field
from typing import Optional


class Todo(BaseModel):

    title: str = Field(min_length=4, description="Title of todo task")

    description: str = Field(min_length=7, description="Description of the task")

    priority: int = Field(gt=0, description="Priority of the task")

    complete: bool = Field(description="Is the task completed? True or False")


# =============================================
# NOTE: Why id is NOT here
# =============================================
# id is auto-assigned by the DB on INSERT (defined in models.py as primary_key).
# Including it here would let users send their own id and potentially overwrite existing rows.
# Rule: the client only sends the data fields -- the DB handles identity (id) itself.
