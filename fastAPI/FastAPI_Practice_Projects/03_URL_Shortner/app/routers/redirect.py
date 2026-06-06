from fastapi import APIRouter, HTTPException, Path, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from utils.db_session import get_db
from datetime import datetime, timezone
from fastapi.responses import RedirectResponse
from utils.logger import log_event
import logging

from models.URL import Url
from starlette import status

router = APIRouter(prefix="/redirect", tags=["redirect"])
DbDependency = Annotated[Session, Depends(get_db)]


@router.get("/{alias}", status_code=status.HTTP_302_FOUND)
def redirect_url(db: DbDependency, alias: str = Path(min_length=6)):
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

    log_event(
        logging.INFO,
        "URL Redirected",
        status_code=status.HTTP_302_FOUND,
    )
    return RedirectResponse(url=get_url.original_url)