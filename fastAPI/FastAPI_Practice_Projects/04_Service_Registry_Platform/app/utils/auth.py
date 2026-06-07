from fastapi import status, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordBearer
from models.user import User as userModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from dependencies import get_db
from jose import jwt, JWTError
from typing import Annotated
from logger import log_event
import logging

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "be59b0a178a9b3130d32a09adf33bf668d7042715f490e46886b37182ed80851"
ALGORITHM = "HS256"
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")
get_token = Annotated[str, Depends(oauth2_bearer)]
DbDependency = Annotated[Session, Depends(get_db)]


# Create and Verify hashed_password
def encrypt_pass(password) -> str:
    return bcrypt_context.hash(password)


def verify_pass(password, hashed_password) -> bool:
    return bcrypt_context.verify(password, hashed_password)


# Encode and Decode JWT Token
def create_jwt(username, id, role) -> str:
    payload = {
        "sub": username,
        "id": str(id),  # UUID is not JSON Serializable.
        "role": role,
    }

    minutes = 20
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload["exp"] = expires

    return jwt.encode(payload, SECRET_KEY, ALGORITHM)


def decode_jwt(jwt_token) -> dict:
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        log_event(
            logging.ERROR, "Invalid token", status_code=status.HTTP_401_UNAUTHORIZED
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user",
        )
    return payload


def authenticate_user(db: DbDependency) -> bool:
    payload = decode_jwt(get_token)

    payload_username: str = payload.get("sub")
    payload_id: str = payload.get("id")
    payload_role: str = payload.get("role")

    if not payload_username or not payload_id:
        log_event(
            logging.ERROR,
            "Missing claims",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate User"
        )

    user = db.query(userModel).filter(userModel.username == payload_username).first()

    if not user == payload_username:
        log_event(
            logging.ERROR, "User not found", status_code=status.HTTP_401_UNAUTHORIZED
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return {"username": payload_username, "id": payload_id, "role": payload_role}
