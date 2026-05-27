from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
class URLResponse(BaseModel):
    short_code: str
    short_url: HttpUrl
    original_url: HttpUrl 
    created_at: datetime 
    expires_at: datetime 

"""
{
  "short_code": "my-link",
  "short_url": "http://localhost:8000/my-link",
  "original_url": "https://www.example.com/very/long/path?query=param",
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-22T10:30:00Z"
}
"""