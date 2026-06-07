from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from models.service import EnvironmentSchema, CurrentStatusSchema
from uuid import UUID
from datetime import datetime


class Service(BaseModel):
    name: str
    team: str
    environment: EnvironmentSchema = Field(default=EnvironmentSchema.DEV)
    health_url: HttpUrl
    webhook_url: HttpUrl | None = None
    current_status: CurrentStatusSchema = Field(default=CurrentStatusSchema.UNKNOWN)
    is_active: bool = Field(default=True)


class ServiceResponse(Service):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    registered_by: UUID
    created_at: datetime
    last_checked_at: datetime | None = None


class ServiceUpdate(BaseModel):
    """All fields optional — only send what you want to update."""
    name: str | None = None
    team: str | None = None
    environment: EnvironmentSchema | None = None
    health_url: HttpUrl | None = None
    webhook_url: HttpUrl | None = None
    is_active: bool | None = None
