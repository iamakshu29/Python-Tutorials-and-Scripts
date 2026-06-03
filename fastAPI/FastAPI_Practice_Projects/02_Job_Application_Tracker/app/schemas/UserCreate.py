from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from models.User import UserRole


class UserCreate(BaseModel):
    email: EmailStr = Field(examples=["abc@mail.com"])
    password: str | None = Field(min_length=3, default=None)
    role: UserRole = Field(examples=["Admin", "User"])


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
