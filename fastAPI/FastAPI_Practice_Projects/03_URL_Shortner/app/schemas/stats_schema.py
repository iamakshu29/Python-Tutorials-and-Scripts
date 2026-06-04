from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class statsSchema(BaseModel):
    short_code: str
    original_url: HttpUrl
    click_count: int = Field(default=0)
    created_at: datetime
    expires_at: datetime
    last_accessed_at: datetime


"""
{
  "short_code": "social_insta_post",
  "original_url": "https://...",
  "click_count": 42,
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-22T10:30:00Z",
  "last_accessed_at": "2024-01-18T14:22:00Z"
}
"""
