from pydantic import BaseModel, EmailStr, Field, ConfigDict
from models.user import UserRoleSchema
from datetime import datetime
from uuid import UUID

class User(BaseModel):
    email: EmailStr
    username: str = Field(min_length=5)
    password: str = Field(min_length=9)
    role: UserRoleSchema

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    role: UserRoleSchema
    created_at: datetime