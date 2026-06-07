# problem is we defined password as str | None but OAuth2PasswordRequestForm has password as requried field
# why we put password as optional or None because we can use the Google OAuth2.0 to authenticate instead of using email and password
# Resolve
# Either create a custom class for form and add fields like
# username: str = Form(...),
# search when creating it.
# most probably the error is due to static typing but we get real error if we not enter the password

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models.User import User
from schemas.UserCreate import UserCreate, Token, UserResponse
from utils.db_session import get_db
from utils.logger import log_event
from uuid import UUID
import logging

router = APIRouter(prefix="/auth", tags=["auth"])

DbDependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Login using email and password to get the JWT Token
UserLoginDep = Annotated[OAuth2PasswordRequestForm, Depends()]

# Takes the API Path which return the JWT Token and Annotate it with String, used for authentication purpose
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")
get_token = Annotated[str, Depends(oauth2_bearer)]

# Attributes to create JWT Token
SECRET_KEY = "be59b0a178a9b3130d32a09adf33bf668d7042715f490e46886b37182ed80851"
ALGORITHM = "HS256"


# Create and return Token with expiration time.
def create_jwt(id: UUID, db: DbDependency) -> str | None:

    # get user_details using the id
    get_details = db.query(User).filter(User.id == id).first()

    if get_details:
        payload = {
            "sub": get_details.email,
            "id": str(id),  # UUID is not JSON Serializable.
            "role": get_details.role,
        }

        # add 20 minutes token expiration time
        minutes = 20
        expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        payload.update({"exp": expires})

        log_event(logging.INFO, f"JWT created and will expire in {minutes} minutes")
        return jwt.encode(payload, SECRET_KEY, ALGORITHM)


# Authenticate User by decoding the Token and match it with Payload values with Registered Users.
def authenticate_user(db: DbDependency, token: get_token) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        log_event(
            logging.ERROR, "Invalid token", status_code=status.HTTP_401_UNAUTHORIZED
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user",
        )

    payload_email: str = payload.get("sub")
    payload_id: str = payload.get("id")
    payload_role: str = payload.get("role")

    if not payload_email or not payload_id:
        log_event(
            logging.ERROR,
            "Missing claims",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate User"
        )

    user = db.query(User).filter(User.email == payload_email).first()

    if not user:
        log_event(
            logging.ERROR, "User not found", status_code=status.HTTP_401_UNAUTHORIZED
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return {"email": payload_email, "id": payload_id, "role": payload_role}


# dict type which contains Payload Values, used for authenticating User when logged in
is_valid = Annotated[dict, Depends(authenticate_user)]


# Adding New User Details in DB with hashed password.
@router.post("/register")
def user_registration_with_email_password(user: UserCreate, db: DbDependency) -> str:
    if user.password:
        hashed_pass = bcrypt_context.hash(user.password)
    try:
        user_data = User(email=user.email, hashed_password=hashed_pass, role=user.role)
        db.add(user_data)
    except SQLAlchemyError as e:
        log_event(
            logging.INFO, "DB Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    except Exception as e:
        log_event(
            logging.INFO,
            "Server Error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    log_event(logging.INFO, "User Created", status_code=status.HTTP_201_CREATED)
    return "User Created Successfully"


# User Login
@router.post("/login", response_model=Token)
def user_login(user: UserLoginDep, db: DbDependency):
    email = user.username
    get_user = db.query(User).filter(User.email == email).first()
    if not get_user:
        log_event(
            logging.ERROR,
            "Authentication Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Either Password or Email is Incorrect",
        )
    decrypt_pass = bcrypt_context.verify(user.password, get_user.hashed_password)
    if not get_user and not decrypt_pass:
        log_event(
            logging.ERROR,
            "Authentication Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Either Password or Email is Incorrect",
        )
    token = create_jwt(get_user.id, db)

    log_event(logging.INFO, "Token Retrieved", status_code=status.HTTP_201_CREATED)
    return {"access_token": token, "token_type": "bearer"}


# @router.get("/google")
# def redirect_to_google():

# @router.get("/google/callback")
# def autheticate_using_google():


@router.get("/me", response_model=UserResponse)
def return_current_user_info(user: is_valid, db: DbDependency):
    if not user:
        log_event(
            logging.ERROR,
            "Authentication Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        get_data = db.query(User).filter(User.id == UUID(user.get("id"))).first()

        log_event(logging.INFO, "Fields Retrieved", status_code=status.HTTP_200_OK)
        return get_data

    except SQLAlchemyError as e:
        log_event(
            logging.INFO, "DB Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DataBase error {e}",
        )
