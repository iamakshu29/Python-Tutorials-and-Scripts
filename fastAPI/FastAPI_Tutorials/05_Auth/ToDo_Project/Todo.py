from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Todo(BaseModel):
    title: str = Field(min_length=4, description="Title of todo task")
    description: str = Field(min_length=7, description="description of the task")
    priority: int = Field(gt=0, description="priority of the task")
    complete: bool = Field(description="is the task Completed True or False")

class Users(BaseModel):
    email: EmailStr = Field(min_length = 3, description="User Email", example="rahul123@gmail.com")
    username: str = Field(min_length = 3, description="username", example="Rahul123")
    first_name: str = Field(min_length = 3, description="User first name", example="Rahul")
    last_name: str = Field(min_length = 3, description="User last name", example="Jain")
    password: str = Field(min_length = 3, description="User Password")
    role: str = Field(min_length = 3, description="User Role")

    