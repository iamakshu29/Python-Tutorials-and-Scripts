from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from sqlalchemy.orm import Session
from utils.db_session import get_db
from models.User import User
from schemas.user_create import UserCreate
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from utils.authenticate import authenticate_user
from passlib.context import CryptContext

router = APIRouter(prefix="/user", tags=["user"])
DbDependency = Annotated[Session, Depends(get_db)]
security = HTTPBasic()
credentials = Annotated[HTTPBasicCredentials, Depends(security)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Create New User
@router.post("/")
def create_user(db: DbDependency, user: UserCreate):
    try:
        hashed_pass = bcrypt_context.hash(user.password)
        # user_create = User(**user.model_dump())
        user_create = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_pass,
            role=user.role,
        )
        db.add(user_create)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB Error {e}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error: {e}")
    return "User Created Successfully"


# Get User details by username and Admin can access all details
@router.get("/")
def get_user_by_username(db: DbDependency, cred: credentials):
    try:
        user = authenticate_user(cred.username, cred.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not Validate User",
                headers={"WWW-Authenticate": "Basic"},
            )
        data = db.query(User).filter(User.username == cred.username).first()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB Error {e}"
        )
    return data


# Upgrade User Membership
@router.patch("/upgrade")
def upgrade_subscription(subscription: str, db: DbDependency, cred: credentials):
    # Auth guard is BEFORE try, so except blocks can't accidentally swallow the 401
    user = authenticate_user(cred.username, cred.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not Validate User",
            headers={"WWW-Authenticate": "Basic"},
        )
    try:
        get_details = db.query(User).filter(User.username == cred.username).first()
        if get_details.subscription_type == "Premium" and subscription == "Premium":
            return "Already has Premium Membership"
        elif get_details.subscription_type == "Premium" and subscription == "Basic":
            return "Downgrade to Basic Membership"
        elif get_details.subscription_type == "Basic" and subscription == "Basic":
            return "Already has Basic Membership"
        else:
            get_details.subscription_type = subscription
            db.commit()
            db.refresh(get_details)
            return "Welcome to Premium Membership"
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB Error {e}"
        )
