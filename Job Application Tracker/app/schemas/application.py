from enum import Enum
from pydantic import BaseModel, Field


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


class JobAppCreate(BaseModel):
    company: str = Field(min_length=2, examples=["EY, SAP, Google"])
    role_title: RoleEnum = Field()
    job_url: str | None = Field(default=None)
    status: StatusEnum = Field()
    notes: str | None = Field(default=None)
