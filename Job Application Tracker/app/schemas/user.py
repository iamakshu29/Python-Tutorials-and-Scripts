from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRoleEnum(str,Enum):
    admin = "Admin"
    user = "User"

class UserCreate(BaseModel):
    email: EmailStr = Field(examples=["abc@mail.com"])
    password: str | None = Field(min_length=3)
    role: UserRoleEnum = Field(examples=["Admin,User"])

class Token(BaseModel):
    access_token: str
    token_type: str
