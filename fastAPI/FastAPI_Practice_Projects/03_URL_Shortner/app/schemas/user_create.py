from pydantic import BaseModel, EmailStr, Field
from models.User import UserRole


class UserCreate(BaseModel):
    email: EmailStr = Field(examples=["abc@mail.com"])
    username: str
    password: str = Field(min_length=7)
    role: UserRole = Field(examples=["Admin,User"])


class Token(BaseModel):
    access_token: str
    token_type: str
