from pydantic import BaseModel
from models.health_check import StatusSchema


class Health(BaseModel):
    status: StatusSchema
    response_time_ms: int
    status_code: int
    error_detail: str | None = None
