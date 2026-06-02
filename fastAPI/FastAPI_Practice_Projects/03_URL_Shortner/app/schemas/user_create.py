from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class UserRole(str,Enum):
    admin = "Admin"
    user = "User"

class UserSubscriptionEnum(str,Enum):
    basic = "Basic"
    premium = "Premium"

class UserCreate(BaseModel):
    email: EmailStr = Field(examples=["abc@mail.com"])
    username: str
    password: str = Field(min_length=7)
    role: UserRole = Field(examples=["Admin,User"])

class Token(BaseModel):
    access_token: str
    token_type: str
