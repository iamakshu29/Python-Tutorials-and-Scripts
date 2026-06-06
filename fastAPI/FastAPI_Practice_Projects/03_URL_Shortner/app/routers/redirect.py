from fastapi import APIRouter, HTTPException, Path, Depends, status, Request
from sqlalchemy.orm import Session
from typing import Annotated
from utils.db_session import get_db
from datetime import datetime, timezone
from fastapi.responses import RedirectResponse
from utils.logger import log_event
import logging

from models.URL import Url
from models.Stats import Stats
from starlette import status

router = APIRouter(prefix="/redirect", tags=["redirect"])
DbDependency = Annotated[Session, Depends(get_db)]


# HOW TO USE:
# Paste this URL directly in your browser address bar (not Swagger):
#   http://localhost:8000/redirect/{urlCode}
# Example: http://localhost:8000/redirect/abc123
#
# The server looks up "abc123" in the DB, finds the original URL,
# and returns a 302 redirect → browser automatically navigates there.
#
# Note: Swagger UI will show the 302 response but won't auto-navigate.
# Always test redirects in a real browser tab.
@router.get("/{alias}", status_code=status.HTTP_302_FOUND)
def redirect_url(request: Request, db: DbDependency, alias: str = Path(min_length=6)):
    get_url = db.query(Url).filter(Url.urlCode == alias).first()

    if not get_url:
        log_event(
            logging.ERROR,
            "URL Not found to redirect",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )

    if get_url.expires_at < datetime.now(timezone.utc):
        log_event(
            logging.ERROR,
            "URL Expired",
            status_code=status.HTTP_410_GONE,
        )
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="URL has expired")

    # Update click count and last accessed time on the URL
    get_url.click_count += 1
    get_url.last_accessed_at = datetime.now(timezone.utc)

    # Log each click as a stats entry
    # referrer = where the user came from (browser sends this automatically)
    # e.g. "https://twitter.com" if they clicked from Twitter, None if typed directly
    stats_data = Stats(
        urlCode=get_url.urlCode,
        referrer=request.headers.get("referer"),  # from browser, not your DB
    )
    db.add(stats_data)
    db.commit()

    log_event(
        logging.INFO,
        "URL Redirected",
        status_code=status.HTTP_302_FOUND,
    )
    return RedirectResponse(url=get_url.original_url)