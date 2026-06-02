from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from uuid import UUID
from datetime import datetime


class StatusEnum(str, Enum):
    applied = "Applied"
    interview = "Interview"
    offer = "Offer"
    rejected = "Rejected"
    ghosted = "Ghosted"


class RoleEnum(str, Enum):
    devops = "Devops"
    developer = "Developer"
    tester = "Tester"


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=2, examples=["EY, SAP, Google"])
    role_title: RoleEnum = Field()
    job_url: HttpUrl | None = None
    status: StatusEnum = Field()
    notes: str | None = Field(default=None)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
