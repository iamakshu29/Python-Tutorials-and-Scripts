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
    title: str = Field(min_length = 3, description="Title of the task", example="Buy Groceries")
    description: str = Field(min_length = 3, description="Description of the task" , example="Buy Carrot, Tomato, Potato")
    status: StatusEnum = Field(min_length = 3, description="Task Status", example="Pending, Completed")
    priority: PriorityEnum = Field(min_length = 3, description="Task Priority Level", example="Low")
    user_id: int = Field(gt=0,description="Id of Different Users",example="101")

class UserCreate(BaseModel):
    name: str = Field(min_length = 3, description="User Name", example="Rahul")
    email: EmailStr = Field(min_length = 3, description="User Email", example="rahul123@gmail.com")