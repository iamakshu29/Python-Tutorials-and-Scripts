from enum import Enum
from pydantic import BaseModel


class StatusEnum(str, Enum):
    applied = "Applied"
    interview = "Interview"
    offer = "Offer"
    rejected = "Rejected"
    ghosted = "Ghosted"


class ApplicationUpdate(BaseModel):
    status: StatusEnum | None = None
    notes: str | None = None
