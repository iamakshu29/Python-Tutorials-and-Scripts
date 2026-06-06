from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from utils.db_session import get_db
from models.URL import Url
from models.User import User
from datetime import datetime, timezone
from schemas.stats_schema import statsSchema
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from utils.authenticate import authenticate_user
from utils.logger import log_event
import logging


router = APIRouter(prefix="/stats", tags=["stats"])
DbDependency = Annotated[Session, Depends(get_db)]
security = HTTPBasic()
credentials = Annotated[HTTPBasicCredentials, Depends(security)]


# Get URL Stats by Alias
@router.get("/{alias}", status_code=status.HTTP_200_OK, response_model=statsSchema)
async def get_stats(db: DbDependency, alias: str, cred: credentials):

    user = authenticate_user(cred.username, cred.password, db)

    if not user:
        log_event(
            logging.ERROR,
            "Could not Validate User",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not Validate User",
            headers={"WWW-Authenticate": "Basic"},
        )

    app_data = db.query(Url).filter(Url.urlCode == alias).first()
    user_data = db.query(User).filter(User.username == cred.username).first()

    if not app_data or user_data.id != app_data.user_id:
        log_event(
            logging.ERROR,
            "Alias not FOund",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alias not found"
        )

    app_data.expires_at = app_data.expires_at.replace(tzinfo=timezone.utc)
    if app_data.expires_at < datetime.now(timezone.utc):
        log_event(
            logging.ERROR,
            "URL expired",
            status_code=status.HTTP_410_GONE,
        )
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="URL expired")

    log_event(logging.INFO, "Stats Generated", status_code=status.HTTP_200_OK)
    return statsSchema(
        original_url=app_data.original_url,
        short_code=app_data.urlCode,
        click_count=app_data.click_count,
        created_at=app_data.created_at,
        expires_at=app_data.expires_at,
        last_accessed_at=app_data.last_accessed_at,
    )

