from fastapi import APIRouter, status, Depends, HTTPException, Path
from models.user import User as userModel
from utils.auth import authenticate_user
from sqlalchemy.orm import Session
from utils.logger import log_event
from dependencies import get_db
from typing import Annotated
from uuid import UUID
import logging


router = APIRouter(prefix="/health", tags=["health"])

DbDependency = Annotated[Session, Depends(get_db)]
is_valid_user = Annotated[dict, Depends(authenticate_user)]


@router.get("/{service_id}/history")
def polls_health_of_a_service(
    db: DbDependency, valid_user: is_valid_user, service_id: UUID = Path()
):
    user = db.query(userModel).filter(userModel.username == valid_user.username).first()
    if not user:
        log_event(
            logging.ERROR,
            "User Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        raise HTTPException(
            detail="User Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    return None
