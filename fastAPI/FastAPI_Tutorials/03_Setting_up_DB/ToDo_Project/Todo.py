from pydantic import BaseModel, Field
from typing import Optional

class Todo(BaseModel):
        title: str = Field(min_length=4,description="Title of todo task")
        description: str = Field(min_length=7,description="description of the task")
        priority: int = Field(gt=0,description="priority of the task")
        complete: bool = Field(description="is the task Completed True or False")

# here the fields are there which are sent by the user to be added in DB
# id is skipped here, as DB set it up automatically in auto-increment fashion by SQLAlchemy not by all ORM or DB
# Why? as we define our id as primary key in models.py for DB schema