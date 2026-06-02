from pydantic import BaseModel
from models.Application import ApplicationStatus

class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    notes: str | None = None
