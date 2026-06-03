from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from uuid import UUID
from datetime import datetime, date
from models.Application import ApplicationStatus, RoleTitle


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=2, examples=["EY, SAP, Google"])
    role_title: RoleTitle = Field(default=RoleTitle.DEVELOPER)
    job_url: HttpUrl | None = None
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED)
    notes: str | None = Field(default=None)

# Get all the fields from ApplicationCreate and add additional fields for response, which we want to return in response after creating application. This is useful when we want to return the created application details in response after creating application.
class ApplicationResponse(ApplicationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    applied_date: date
    created_at: datetime
    updated_at: datetime


class StatsResponse(BaseModel):
    total_applications: int
    status: dict[str, int]
    top_companies: list[str]
