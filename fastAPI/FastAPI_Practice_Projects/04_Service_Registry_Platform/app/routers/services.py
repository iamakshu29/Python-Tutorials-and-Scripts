from fastapi import APIRouter, status, Depends, HTTPException, Path
from models.service import Service as serviceModel
from schemas.service import Service as serviceSchema, ServiceResponse, ServiceUpdate
from models.user import User as userModel
from utils.auth import authenticate_user
from sqlalchemy.orm import Session
from utils.logger import log_event
from dependencies import get_db
from typing import Annotated
from uuid import Uuid
import logging

router = APIRouter(prefix="/services", tags=["services"])

DbDependency = Annotated[Session, Depends(get_db)]
is_valid_user = Annotated[dict, Depends(authenticate_user)]


@router.post("/")
def register_new_service(
    db: DbDependency, serviceBody: serviceSchema, login: is_valid_user
):
    user = db.query(userModel).filter(userModel.username == login.username).first()
    if not user:
        log_event(
            logging.ERROR,
            "User Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        raise HTTPException(
            detail="User Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    service = serviceModel(serviceBody.model_dump())
    db.add(service)
    return "Service Created Successfully"


@router.get("/", response_model=list[ServiceResponse])
def list_all_services(db: DbDependency, valid_user: is_valid_user):
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
    services = db.query(serviceModel).all()
    return services


@router.get("/{id}", response_model=ServiceResponse)
def get_service_details_and_status(
    db: DbDependency, valid_user: is_valid_user, id: Uuid = Path()
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
    service = db.query(serviceModel).filter(serviceModel.id == id).first()
    return service


@router.patch("/{id}", response_model=ServiceResponse)
def update_service_config(
    db: DbDependency, service_update: ServiceUpdate, valid_user: is_valid_user
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
    service = db.query(serviceModel).filter(serviceModel.id == id).first()
    update_service = ServiceUpdate.model_dump(exclude_unset=True)
    for key, value in update_service.items():
        setattr(service, key, value)

    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{id}")
def deregister_a_service(db: DbDependency, valid_user: is_valid_user):
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
    service = db.query(serviceModel).filter(serviceModel.id == id).first()
    service.is_active = False
    db.refresh(service)
    return f"{service.name} Service from environment: {service.env} deregistered by team: {service.team}"


@router.post("/{id}/check")
def trigger_health_check_to_a_service(db: DbDependency, valid_user: is_valid_user):
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
    service = db.query(serviceModel).filter(serviceModel.id == id).first()
    service.health_url = f"http://{service.name}/health"
    return "Triggering Health check"
