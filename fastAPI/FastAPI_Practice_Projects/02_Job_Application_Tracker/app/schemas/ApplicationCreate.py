from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from uuid import UUID
from datetime import datetime
from models.Application import ApplicationStatus, RoleTitle

class ApplicationCreate(BaseModel):
    company: str = Field(min_length=2, examples=["EY, SAP, Google"])
    role_title: RoleTitle = Field()
    job_url: HttpUrl | None = None
    status: ApplicationStatus = Field()
    notes: str | None = Field(default=None)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
