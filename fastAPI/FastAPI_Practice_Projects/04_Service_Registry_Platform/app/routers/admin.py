from fastapi import APIRouter, status, Depends, HTTPException, Path
from typing import Annotated
from schemas.user import User as UserResponse
from models.user import User as userModel
from models.service import User as serviceModel
from schema.service import ServiceResponse
from utils.auth import authenticate_user
from sqlalchemy.orm import Session
from dependencies import get_db
import logging
from uuid import Uuid
from utils.logger import log_event

router = APIRouter(prefix="/admin", tags=["admin"])
DbDependency = Annotated[Session, Depends(get_db)]
is_valid_user = Annotated[dict, Depends(authenticate_user)]


def verify_admin_user(valid_user: is_valid_user, db: DbDependency):
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

    if user.role != "admin":  # Cleaned up 'not user.role == "admin"' to '!= "admin"'
        log_event(
            logging.ERROR,
            "User does not have Admin privileges",
            status_code=status.HTTP_403_FORBIDDEN,
        )
        raise HTTPException(detail="User Not Found", status_code=status.HTTP_403)

    return user


is_admin = Annotated[userModel, Depends(verify_admin_user)]


@router.get(
    "/services", response_model=list[ServiceResponse], status_code=status.HTTP_200_OK
)
def get_all_services(db: DbDependency, current_user: is_admin):
    return db.query(serviceModel).all()


@router.get("/users", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def get_all_registered_users(db: DbDependency, current_user: is_admin):
    return db.query(userModel).all()


@router.patch("/services/{id}/deactivate")
def force_deactivate_a_service_by_id(
    db: DbDependency,
    current_user: is_admin,
    id: Uuid = Path(default=Uuid),
):
    service = db.query(serviceModel).filter(serviceModel.id == id).first()
    service.is_active = False

    db.refresh(service)

    return f"{service.name} Service Deactivated"
