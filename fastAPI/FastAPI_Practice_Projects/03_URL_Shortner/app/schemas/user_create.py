from pydantic import BaseModel, EmailStr, Field
from models.User import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    role: str
    subscription_type: str


class Token(BaseModel):
    access_token: str
    token_type: str
