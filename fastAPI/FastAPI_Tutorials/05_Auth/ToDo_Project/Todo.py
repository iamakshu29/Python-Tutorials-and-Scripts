# Todo.py -- Pydantic request/response models
# Pydantic validates and parses data BEFORE it reaches route logic.
# If validation fails, FastAPI automatically returns HTTP 422 Unprocessable Entity.
# These models are separate from models.py (SQLAlchemy) — one is for HTTP data, the other for DB schema.

# BaseModel - base class for all Pydantic models; enables automatic validation + serialization
# Field     - adds validation rules and Swagger UI metadata (description, example, constraints)
# EmailStr  - a special Pydantic string type that validates the value is a proper email format
#             requires: pip install pydantic[email]
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


# =============================================
# Todo - request body model for creating/updating a todo
# =============================================
class Todo(BaseModel):
    title: str = Field(min_length=4, description="Title of todo task")
    description: str = Field(min_length=7, description="description of the task")
    priority: int = Field(gt=0, description="priority of the task")
    complete: bool = Field(description="is the task Completed True or False")
    # id and owner are NOT here — id is auto-assigned by DB, owner is taken from the JWT token


# =============================================
# Users - request body model for user registration (POST /auth/)
# =============================================
class Users(BaseModel):
    # EmailStr validates format like "user@example.com" — rejects "notanemail"
    email: EmailStr = Field(min_length=3, description="User Email", example="rahul123@gmail.com")
    username: str = Field(min_length=3, description="username", example="Rahul123")
    first_name: str = Field(min_length=3, description="User first name", example="Rahul")
    last_name: str = Field(min_length=3, description="User last name", example="Jain")
    # "password" here is the plain-text password sent by the user
    # auth.py hashes it with bcrypt before saving — the DB never sees the plain password
    password: str = Field(min_length=3, description="User Password")
    role: str = Field(min_length=3, description="User Role")  # e.g. "admin" or "user"


# =============================================
# Token - response model for POST /auth/token (login endpoint)
# =============================================
# response_model=Token in auth.py ensures the /token route always returns this exact shape
# access_token -> the JWT string the client must send in subsequent requests
# token_type   -> "bearer" (OAuth2 standard) — client sends it as: Authorization: Bearer <token>
class Token(BaseModel):
    access_token: str
    token_type: str