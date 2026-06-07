from utils.auth import encrypt_pass, verify_pass, create_jwt, authenticate_user
from fastapi import APIRouter, status, Depends, HTTPException
from schemas.user import User as userSchema, UserResponse
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User as userModel
from sqlalchemy.orm import Session
from utils.logger import log_event
from dependencies import get_db
from typing import Annotated
import logging

router = APIRouter(prefix="/auth", tags=["auth"])

login_details = Annotated[OAuth2PasswordRequestForm, Depends()]
DbDependency = Annotated[Session, Depends(get_db)]

is_valid_user = Annotated[dict, Depends(authenticate_user)]


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_new_user(db: DbDependency, user_request: userSchema):
    hashed_password = encrypt_pass(user_request.password)

    user_data = userModel(
        email=user_request.email,
        username=user_request.username,
        hashed_password=hashed_password,
        role=user_request.role,
    )

    db.add(user_data)

    log_event(
        logging.INFO,
        "User Registered Successfully...",
        status_code=status.HTTP_201_CREATED,
    )

    return "User Registered Successfully..."


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(db: DbDependency, userLogin: login_details):

    user = db.query(userModel).filter(userModel.username == userLogin.username).first()

    if not user:
        log_event(
            logging.ERROR,
            "User Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

        raise HTTPException(
            detail="User Not Found", status_code=status.HTTP_404_NOT_FOUND
        )

    if not verify_pass(userLogin.password, user.hashed_password):
        log_event(
            logging.ERROR,
            "User Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

        raise HTTPException(
            detail="Either Password or Username is wrong",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    jwt_token = create_jwt(user.usename, user.id, user.role)

    log_event(logging.INFO, "Token Retrieved", status_code=status.HTTP_201_CREATED)
    return {"access_token": jwt_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_info(db: DbDependency, valid_user: is_valid_user):

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

    return user
