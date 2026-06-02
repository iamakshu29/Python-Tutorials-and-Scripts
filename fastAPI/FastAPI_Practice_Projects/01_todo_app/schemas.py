# Pydantic Model
from enum import Enum
from datetime import date
from pydantic import BaseModel, Field, EmailStr

class StatusEnum(str,Enum):
    pending = "Pending"
    in_progress = "In Progress"
    completed = "Completed"

class PriorityEnum(str,Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class TodoCreate(BaseModel):
    title: str = Field(min_length = 3, description="Title of the task", examples=["Buy Groceries"])
    description: str = Field(min_length = 3, description="Description of the task" , examples=["Buy Carrot, Tomato, Potato"])
    status: StatusEnum = Field(min_length = 3, description="Task Status", examples=["Pending, Completed"])
    priority: PriorityEnum = Field(min_length = 3, description="Task Priority Level", examples=["Low"])
    user_id: int = Field(gt=0,description="Id of Different Users",examples=["101"])

class UserCreate(BaseModel):
    name: str = Field(min_length = 3, description="User Name", examples=["Rahul"])
    username: str = Field(min_length = 3, description="username", examples=["Rahul123"])
    email: EmailStr = Field(min_length = 3, description="User Email", examples=["rahul123@gmail.com"])
    password: str = Field(min_length=3, description="Enter Password")
    role: str = Field(min_length=3, description="User Role")
