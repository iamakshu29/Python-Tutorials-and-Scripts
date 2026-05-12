# routers/auth.py -- Authentication router
# Handles: user registration, listing users, login (token generation)
# This is a router file — not the main app. See routers/router.md for the full router concept.

# APIRouter  - creates a mini-app with its own routes; gets included into main.py via include_router()
# Depends    - FastAPI dependency injection (used to inject get_db session into routes)
# HTTPException - raises HTTP errors with a status code and message
# Path, Query - validate path and query parameters
from jose import JWTError
from datetime import timezone
from fastapi import APIRouter, Depends, HTTPException, Path, Query

# Users - Pydantic model for validating the create-user request body (from Todo.py)
from Todo import Users, Token
from db import SessionLocal
from typing import Annotated
from starlette import status

# User - the SQLAlchemy model representing the "users" table in the DB
from models import User

# SQLAlchemyError - base exception class for all SQLAlchemy DB errors
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# CryptContext - passlib wrapper that manages hashing algorithms
#                we use it to hash passwords on registration and verify them on login
from passlib.context import CryptContext

from datetime import datetime, timedelta

from jose import jwt # It needs a secret and an algorithm to create JWT

# openssl rand -hex 32
SECRET_KEY = "718e92cf9c2471684d003f9860f8cd3f6ac2c78596ca5789b239bc28a7cf6c65"

ALGORITHM = "HS256"

# OAuth2PasswordRequestForm - a built-in FastAPI form class for username/password login
# Explain OAuth2PasswordBearer 
# it expects the request as multipart form data (not JSON), which is the OAuth2 standard
# python-multipart must be installed for FastAPI to parse form data -> pip install python-multipart
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# =============================================
# ROUTER SETUP
# =============================================
# APIRouter() creates an isolated router — its routes are registered here
# and then attached to the main FastAPI app in main.py via app.include_router(auth.router)

# explain prefix and tags
router = APIRouter(
    prefix = "/auth", tags = ["auth"]
)

# CryptContext configures the hashing setup
# schemes=['bcrypt'] -> use bcrypt as the hashing algorithm (industry standard for passwords)
# deprecated="auto"  -> if a password was hashed with an older/weaker algorithm,
#                       passlib will flag it as deprecated (so you can re-hash it on next login)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

# explain this
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db            # provide the session to the route function
        db.commit()         # persist changes if route completed without error
    except SQLAlchemyError as e:
        db.rollback()       # undo any partial DB changes on DB error
        raise HTTPException(status_code=500, detail=f"DB commit failed: {e}")
    finally:
        db.close()          # always release the session back to the pool

# reusable type alias: injects a DB session into any route that declares db: DbDependency
DbDependency = Annotated[Session, Depends(get_db)]


# =============================================
# GET /auth -> list all users
# =============================================
@router.get("/")
async def get_user(db: DbDependency):
    try:
        users_data = db.query(User).all()  # fetch all rows from the users table
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    return {"user": users_data}


# =============================================
# POST /auth -> register a new user
# =============================================
@router.post("/")
async def create_user(create_user_req: Users, db: DbDependency) -> str:
    # Note: we can't do User(**create_user_req.dict()) directly because
    # the Pydantic field is named "password" but the DB column is "hashed_password"
    # so we map each field manually and hash the password before saving
    try:
        # hash the plain-text password using bcrypt before storing it
        # bcrypt produces a different hash every time (salted) but verify() still works
        # NEVER store plain-text passwords in a DB
        hashed_pwd = bcrypt_context.hash(create_user_req.password)

        user_data = User(
            email=create_user_req.email,
            username=create_user_req.username,
            first_name=create_user_req.first_name,
            last_name=create_user_req.last_name,
            hashed_password=hashed_pwd,   # store the hash, not the raw password
            role=create_user_req.role
        )
        db.add(user_data)  # stage the new user row; committed in get_db() after route finishes
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    return "User Added Successfully"


# =============================================
# HELPER: authenticate_user
# =============================================
# called by the /token route to verify credentials before issuing a token
# returns True if the user exists and the password matches, False otherwise
def authenticate_user(username, password, db):
    try:
        # query the users table for a row matching the given username
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False  # username not found in DB

        # bcrypt_context.verify(plain_password, hashed_password)
        # internally: hashes the plain_password the same way and compares with stored hash
        # returns False if they don't match (wrong password)
        if not bcrypt_context.verify(password, user.hashed_password):
            return False
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    return user  # credentials are valid

def create_JWT(username: str,user_id: int, role: str, expires_delta: timedelta) -> str:
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update ({"exp":expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: int = payload.get("role")
        
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate User")
        
        return {"username": username, "user_id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate User")

# =============================================
# POST /token -> login and receive a JWT
# =============================================
# OAuth2PasswordRequestForm expects form fields: username and password (not JSON body)
# Depends() with no argument means FastAPI instantiates OAuth2PasswordRequestForm automatically

# explain the second arg in post decorator
@router.post("/token",response_model = Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbDependency
):
    # step 1: verify the credentials against the DB
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        # 401 Unauthorized -> credentials are wrong or user doesn't exist
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate User")

    token = create_JWT(user.username, user.id, user.role, timedelta(minutes=20))

    # step 2: credentials are valid -> generate and return a JWT
    return {"access_token": token, "token_type": "bearer"}
    
