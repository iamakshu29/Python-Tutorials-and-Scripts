from pydantic import BaseModel, Httpurl, Field
from model.service import EnvironmentSchema, CurrentStatusSchema
from uuid import UUID
from datetime import datetime


class Service(BaseModel):
    name: str
    team: str
    environment: EnvironmentSchema = Field(default="dev")
    health_url: Httpurl
    webhook_url: Httpurl | None = None
    current_status: CurrentStatusSchema
    is_active: bool = Field(default=True)


class ServiceResponse(Service):
    id: UUID
    registered_by: UUID
    created_at: datetime
    last_checked_at: datetime


class ServiceUpdate(Service):
    pass
