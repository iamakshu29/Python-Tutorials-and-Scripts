from pydantic import BaseModel, Field


class Todo(BaseModel):
    title: str = Field(min_length=4, description="Title of todo task")
    description: str = Field(min_length=7, description="Description of the task")
    priority: int = Field(gt=0, description="Priority of the task")
    complete: bool = Field(description="Is the task completed? True or False")
