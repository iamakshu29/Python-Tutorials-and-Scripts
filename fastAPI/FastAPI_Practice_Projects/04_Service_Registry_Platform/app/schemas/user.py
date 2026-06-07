from pydantic import BaseModel, EmailStr, Field
from models.user import UserRoleSchema
from datetime import datetime
from uuid import UUID

class User(BaseModel):
    email: EmailStr
    username: str = Field(min_length=5)
    password: str = Field(min_length=9)
    role: UserRoleSchema

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    role: UserRoleSchema
    create_at: datetime