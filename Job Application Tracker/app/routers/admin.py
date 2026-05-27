from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from routers.auth import authenticate_user
from models.Application import Application
from models.User import User
from schemas.application import StatusEnum
from sqlalchemy.orm import Session
from utils.db_session import get_db
from utils.logger import log_event
import logging
from starlette import status

router = APIRouter(prefix="/admin", tags=["admin"])

DbDependency = Annotated[Session, Depends(get_db)]
valid_user = Annotated[dict, Depends(authenticate_user)]


# list all user details to admin user
@router.get("/users")
def list_users(user: valid_user, db: DbDependency):
    if not user:
        log_event(
            logging.ERROR,
            "Authentication Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    if user.get("role") != "Admin":
        log_event(
            logging.INFO,
            "User Not Authorized",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Authorized"
        )

    get_users = db.query(User).all()

    log_event(logging.INFO, "Fields Retrieved", status_code=status.HTTP_200_OK)
    return get_users


# list all application details to admin user
@router.get("/applications")
def list_all_applications(user: valid_user, db: DbDependency):
    if user.get("role") != "Admin":
        log_event(
            logging.INFO,
            "User Not Authorized",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(status_code=403, detail="User Not Authorized")

    get_applications = db.query(Application).all()

    log_event(logging.INFO, "Fields Retrieved", status_code=status.HTTP_200_OK)
    return get_applications


@router.get("/stats")
def get_application_stats(user: valid_user, db: DbDependency):
    if user.get("role") != "Admin":
        log_event(
            logging.ERROR,
            "User Not Authorized",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(status_code=403, detail="User Not Authorized")

    response = {
        "total_applications": db.query(Application).count(),
        "status": {},
        "top_companies": [],
    }

    for i in StatusEnum:
        response["status"][i.value] = (
            db.query(Application).filter(Application.status == i.value).count()
        )

    company_hash = {}

    # When iterated by row, it is usually a tuple-like row object not list
    for row in db.query(Application.company):
        company = row[0]  # getting 0th index value of tuple
        company_hash[company] = company_hash.get(company, 0) + 1  # hashing

    top_5_companies = dict(
        sorted(company_hash.items(), key=lambda x: x[1], reverse=True)[:5]
    )

    response["top_companies"].extend(top_5_companies.keys())

    log_event(logging.INFO, "Status Retrieved", status_code=status.HTTP_200_OK)
    return response
