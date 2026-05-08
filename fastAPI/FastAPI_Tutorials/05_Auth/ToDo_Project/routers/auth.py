from fastapi import APIRouter, Depends, HTTPException, Path, Query
from Todo import Users
from db import SessionLocal
from typing import Annotated
from models import User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
# to encode
import base64
# to hash using HMACSHA256 algo
import hmac
import hashlib
import json

# OAuth2 password request form, what the use of installing python-multipart here?
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated="auto")

def get_db():
    db = SessionLocal()   
    try:
        yield db          
        db.commit()       
    except SQLAlchemyError as e:
        db.rollback()     
        raise HTTPException(status_code=500, detail=f"DB commit failed: {e}")          
    finally:
        db.close()
DbDependency = Annotated[Session, Depends(get_db)]

@router.get("/auth")
async def get_user(db: DbDependency):
    try:
        users_data = db.query(User).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    return {"user":users_data}

@router.post("/auth")
async def create_user(create_user_req: Users,db: DbDependency) -> str:
    # user_data = User(**create_user_req.dict()) # skipping this as one of the attribute doesnot have same name as DB column Name in Pydantic Attribute.
    # So expanding each attribute and assigning the value inside during Object creation
    try:
        hashed_pwd = bcrypt_context.hash(create_user_req.password)
        user_data = User(
            email=create_user_req.email,
            username=create_user_req.username,
            first_name=create_user_req.first_name,
            last_name=create_user_req.last_name,
            # hashed_password=create_user_req.password,
            hashed_password=hashed_pwd,
            role=create_user_req.role
        )
        db.add(user_data)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    return "User Added Successfully"

def authenticate_user(username, password, db) -> bool:
# return matched row
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
# bcrypt_context.verify(plain_password, hashed_password)
        if not bcrypt_context.verify(password,user.hashed_password):
            return False
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")
    return True

def create_JWT(username, db) -> str :
    JWT_header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    try:
        user = db.query(User).filter(User.username == username).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")
    
    JWT_payload = {
        "sub": str(datetime.utcnow()),
        "name": user.first_name + " " + user.last_name,
        "given_name": user.first_name,
        "family_name": user.last_name,
        "email": user.email,
        "admin": user.role == "admin"
    }

    header_json = json.dumps(JWT_header, separators=(",", ":")).encode()
    payload_json = json.dumps(JWT_payload, separators=(",", ":")).encode()
    secret = b"learningapi"

# Base64URL encode
    header_b64 = base64.urlsafe_b64encode(header_json).rstrip(b"=")
    payload_b64 = base64.urlsafe_b64encode(payload_json).rstrip(b"=")
# Create signing input
    message = header_b64 + b"." + payload_b64
# HMAC-SHA256 signature
    signature = hmac.new(secret,message,hashlib.sha256).digest()
# Base64URL encode signature
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=")
    jwt_token = (
        message + b"." + signature_b64
    ).decode()
# JWT format
# base64url(header).base64url(payload).base64url(signature)
    return jwt_token

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbDependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    return create_JWT(form_data.username, db)
    
