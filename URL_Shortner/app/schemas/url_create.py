from pydantic import BaseModel, HttpUrl, Field


class URLCreate(BaseModel):
    original_url: HttpUrl = Field(min_length=10)
    urlCode: str | None = Field(min_length=7, max_length=7, default=None)
    expires_in: int | None = Field(default=None)
