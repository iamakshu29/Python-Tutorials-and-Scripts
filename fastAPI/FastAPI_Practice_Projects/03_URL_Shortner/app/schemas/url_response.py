from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict
from uuid import UUID


class URLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    urlCode: str
    original_url: HttpUrl
    created_at: datetime
    last_accessed_at: datetime
    expires_at: datetime
    expired: bool


class BulkURLResponse(BaseModel):
    urlCode: str
    original_url: HttpUrl
    created_at: datetime
    expires_at: datetime
    last_accessed_at: datetime
    user_id: UUID
