# routers/auth.py -- Authentication router
# Handles: user registration, listing users, login (JWT token generation), token decoding
# This is a router file — not the main app. See routers/router.md for the full router concept.
# For how JWT works internally step by step, see: auth copy.py

# jwt (python-jose) - handles JWT encode and decode
# pip install python-jose
# jwt.encode(payload, secret, algorithm) -> creates a signed token string
# jwt.decode(token, secret, algorithms)  -> validates and extracts the payload
from jose import jwt, JWTError
# JWTError  - exception raised by python-jose when a token is invalid, expired, or tampered

# timedelta - used to calculate the token expiry time (e.g. now + 20 minutes)
from datetime import timezone, datetime, timedelta

# APIRouter  - creates a mini-app with its own routes; gets included into main.py via include_router()
# Depends    - FastAPI dependency injection
# HTTPException - raises HTTP errors with a status code and message
from fastapi import APIRouter, Depends, HTTPException

# Users  - Pydantic model for validating the create-user request body
# Token  - Pydantic model for the /token response body (access_token + token_type)
from Todo import Users, Token

from db import SessionLocal
from typing import Annotated
from starlette import status

# User - the SQLAlchemy model representing the "users" table in the DB
from models import User

# SQLAlchemyError - exception raised by SQLAlchemy on DB errors (e.g. connection issues, query errors)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# CryptContext - passlib wrapper that manages password hashing and verification
from passlib.context import CryptContext


# =============================================
# JWT CONFIG
# =============================================
# SECRET_KEY - used to sign and verify the JWT signature
# Generate a strong key with command: 
#   openssl rand -hex 32
# In production: store in environment variables, NEVER hardcode in source code
SECRET_KEY = "718e92cf9c2471684d003f9860f8cd3f6ac2c78596ca5789b239bc28a7cf6c65"

# ALGORITHM - the signing algorithm; HS256 = HMAC + SHA256 (most common for JWTs)
ALGORITHM = "HS256"

# OAuth2PasswordRequestForm - FastAPI's built-in form class for username/password login
#   expects the request body as multipart FORM DATA (not JSON) — this is the OAuth2 standard
#   requires: pip install python-multipart (FastAPI uses it to parse form fields)
#
# OAuth2PasswordBearer - a FastAPI security dependency that:
#   1. tells FastAPI this app uses OAuth2 with password flow (automatically adds the Authorize button in the Swagger UI)
#   2. automatically extracts the Bearer token from the Authorization header on each request by pointing to tokenUrl endpoint which returns the token. In this case,
#   tokenUrl="auth/token" -> points to the login endpoint that issues tokens
#                            Swagger UI uses this to know where to send the login form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# =============================================
# ROUTER SETUP
# =============================================
# APIRouter() creates an isolated router that can have its own routes, dependencies, and tags.
# and then we include this router in the main app (main.py) to combine it with other routers via app.include_router(auth.router)

# prefix="/auth"  -> all routes in this router are automatically prefixed with /auth
#                    e.g. @router.get("/") becomes GET /auth/
#                         @router.post("/token") becomes POST /auth/token
#                    avoids repeating "/auth" in every route definition
# tags=["auth"]   -> groups all routes under "auth" in Swagger UI (/docs)
#                    purely cosmetic — helps organise the docs page
router = APIRouter(
    prefix="/auth", tags=["auth"]
)

# CryptContext configures the hashing setup
# schemes=['bcrypt'] -> use bcrypt as the hashing algorithm (industry standard for passwords)
# deprecated="auto"  -> if a password was hashed with an older/weaker algorithm,
#                       passlib will flag it as deprecated so you can re-hash it on next login
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

# OAuth2PasswordBearer instance used as a dependency in get_current_user
# when a route declares: token: Annotated[str, Depends(oauth2_bearer)]
# FastAPI automatically reads the Authorization: Bearer <token> header and extracts the token string
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

def create_JWT(username: str, user_id: int, role: str, expires_delta: timedelta) -> str:
    # build the payload (claims) to encode into the token
    # "sub" (subject) -> standard JWT claim, here we store the username
    # "id"            -> custom claim: the user's DB primary key (used in todos/admin to filter by owner)
    # "role"          -> custom claim: "admin" or "user" (used for access control in admin.py)
    payload = {"sub": username, "id": user_id, "role": role}

    # calculate expiry time: current UTC time + the given timedelta (e.g. 20 minutes)
    # timezone.utc makes it timezone-aware, which is required by python-jose for "exp"
    expires = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp": expires})  # add "exp" claim; jose will auto-reject expired tokens on decode

    # jwt.encode(payload, secret, algorithm) -> signs and returns the token string
    # python-jose handles Base64URL encoding, JSON serialization, and HMAC signing internally
    # see jwt_internals.py to understand what this does step by step manually
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    # this function is a FastAPI dependency used by todos, admin, and users routers
    # it runs BEFORE every protected route, extracts and validates the JWT from the request header
    # if valid -> returns a dict with the user's info for the route to use
    # if invalid -> raises 401 so the route never executes
    try:
        # jwt.decode() does three things:
        # 1. verifies the signature (was it signed with our SECRET_KEY?)
        # 2. checks expiry ("exp" claim - raises JWTError if token has expired)
        # 3. decodes and returns the payload as a dict
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # extract our custom claims from the decoded payload
        username: str = payload.get("sub")   # the username we encoded at login
        user_id: int = payload.get("id")     # the user's DB id we encoded at login
        user_role: str = payload.get("role") # "admin" or "user"

        # if either core claim is missing, the token is malformed -> reject it
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate User")

        # return a plain dict — this is what user_dependency receives in protected routes
        return {"username": username, "user_id": user_id, "user_role": user_role}

    except JWTError:
        # catches: expired tokens, invalid signature, malformed token, wrong algorithm
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate User")

# =============================================
# POST /auth/token -> login and receive a JWT
# =============================================
# OAuth2PasswordRequestForm -> expects form data with "username" and "password" fields (not JSON request body)
# Depends() -> FastAPI dependency injection; with no arguement, it will look for the declared dependency (OAuth2PasswordRequestForm) and provide its result as the argument value

# response_model=Token -> FastAPI validates the return value against the Token Pydantic model
#                         and strips any extra fields before sending the response
#                         also makes the response schema visible in Swagger UI docs
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbDependency
):
    # step 1: verify the credentials against the DB
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        # 401 Unauthorized -> wrong username or wrong password
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not Validate User")

    # step 2: credentials are valid -> create a JWT valid for 20 minutes
    token = create_JWT(user.username, user.id, user.role, timedelta(minutes=20))

    # step 3: return the token wrapped in the Token Pydantic model shape
    # "bearer" is the OAuth2 token type — client must send it as: Authorization: Bearer <token>
    return {"access_token": token, "token_type": "bearer"}
    
