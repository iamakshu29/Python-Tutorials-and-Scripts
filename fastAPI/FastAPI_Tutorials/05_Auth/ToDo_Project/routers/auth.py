# routers/auth.py -- Authentication router
# Handles: user registration, listing users, login (token generation)
# This is a router file — not the main app. See routers/router.md for the full router concept.

# APIRouter  - creates a mini-app with its own routes; gets included into main.py via include_router()
# Depends    - FastAPI dependency injection (used to inject get_db session into routes)
# HTTPException - raises HTTP errors with a status code and message
# Path, Query - validate path and query parameters
from fastapi import APIRouter, Depends, HTTPException, Path, Query

# Users - Pydantic model for validating the create-user request body (from Todo.py)
from Todo import Users
from db import SessionLocal
from typing import Annotated

# User - the SQLAlchemy model representing the "users" table in the DB
from models import User

# SQLAlchemyError - base exception class for all SQLAlchemy DB errors
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# CryptContext - passlib wrapper that manages hashing algorithms
#                we use it to hash passwords on registration and verify them on login
from passlib.context import CryptContext

from datetime import datetime

# base64 - used to Base64URL encode the JWT header and payload
import base64

# hmac + hashlib - used together to create the HMAC-SHA256 signature for the JWT
# hmac    -> the HMAC algorithm (Hash-based Message Authentication Code)
# hashlib -> provides sha256 as the underlying hash function
import hmac
import hashlib

# json - used to serialize the JWT header and payload dicts into JSON strings before encoding
import json

# OAuth2PasswordRequestForm - a built-in FastAPI form class for username/password login
# it expects the request as multipart form data (not JSON), which is the OAuth2 standard
# python-multipart must be installed for FastAPI to parse form data -> pip install python-multipart
from fastapi.security import OAuth2PasswordRequestForm

# =============================================
# ROUTER SETUP
# =============================================
# APIRouter() creates an isolated router — its routes are registered here
# and then attached to the main FastAPI app in main.py via app.include_router(auth.router)
router = APIRouter()

# CryptContext configures the hashing setup
# schemes=['bcrypt'] -> use bcrypt as the hashing algorithm (industry standard for passwords)
# deprecated="auto"  -> if a password was hashed with an older/weaker algorithm,
#                       passlib will flag it as deprecated (so you can re-hash it on next login)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

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
@router.get("/auth")
async def get_user(db: DbDependency):
    try:
        users_data = db.query(User).all()  # fetch all rows from the users table
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    return {"user": users_data}


# =============================================
# POST /auth -> register a new user
# =============================================
@router.post("/auth")
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
def authenticate_user(username, password, db) -> bool:
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

    return True  # credentials are valid


# =============================================
# HELPER: create_JWT (manual implementation - for learning purposes)
# =============================================
# This manually builds a JWT from scratch to understand the internal mechanics.
# In real projects, use python-jose: pip install python-jose
#   from jose import jwt
#   token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
# See jwt_utils.py for a fully commented step-by-step breakdown of this manual approach.
def create_JWT(username, db) -> str:
    # JWT has 3 parts: Header . Payload . Signature (all Base64URL encoded)
    JWT_header = {
        "alg": "HS256",   # signing algorithm
        "typ": "JWT"      # token type
    }
    try:
        user = db.query(User).filter(User.username == username).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    # payload (also called "claims") - the actual data we want to encode in the token
    # sub (subject) - typically the user identifier; here using timestamp (replace with user id in prod)
    JWT_payload = {
        "sub": str(datetime.utcnow()),
        "name": user.first_name + " " + user.last_name,
        "given_name": user.first_name,
        "family_name": user.last_name,
        "email": user.email,
        "admin": user.role == "admin"  # True if role is "admin", else False
    }

    # serialize dicts to compact JSON (no spaces) then encode to bytes for processing
    header_json = json.dumps(JWT_header, separators=(",", ":")).encode()
    payload_json = json.dumps(JWT_payload, separators=(",", ":")).encode()

    secret = b"learningapi"  # signing secret (in production, load from env variable, never hardcode)

    # Base64URL encode: standard base64 but uses - and _ instead of + and /
    # rstrip(b"=") removes padding ("=") since JWT spec doesn't use it
    header_b64 = base64.urlsafe_b64encode(header_json).rstrip(b"=")
    payload_b64 = base64.urlsafe_b64encode(payload_json).rstrip(b"=")

    # the "signing input" is: base64url(header) + "." + base64url(payload)
    message = header_b64 + b"." + payload_b64

    # HMAC-SHA256: signs the message using the secret key
    # this produces a unique, verifiable signature that can't be forged without the secret
    signature = hmac.new(secret, message, hashlib.sha256).digest()

    # Base64URL encode the raw signature bytes
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=")

    # final JWT: header.payload.signature (all Base64URL encoded, separated by dots)
    jwt_token = (message + b"." + signature_b64).decode()

    return jwt_token


# =============================================
# POST /token -> login and receive a JWT
# =============================================
# OAuth2PasswordRequestForm expects form fields: username and password (not JSON body)
# Depends() with no argument means FastAPI instantiates OAuth2PasswordRequestForm automatically
@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbDependency
):
    # step 1: verify the credentials against the DB
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        # 401 Unauthorized -> credentials are wrong or user doesn't exist
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # step 2: credentials are valid -> generate and return a JWT
    return create_JWT(form_data.username, db)
    
