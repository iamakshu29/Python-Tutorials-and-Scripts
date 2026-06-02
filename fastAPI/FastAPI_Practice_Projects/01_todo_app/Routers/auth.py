from datetime import datetime
from DB.models import Users
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from starlette import status
from fastapi import APIRouter, Path, Query, HTTPException, Depends
from schemas import UserCreate
from DB.models import Todos
from DB.db import SessionLocal
import base64
import hmac
import hashlib
import json


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

@router.get("/users")
async def get_users(db: DbDependency,):
    user_data = db.query(Users).all()
    return user_data

@router.post("/user")
async def create_user(
    db:DbDependency,
    user: UserCreate
):
    try:
        hashed_pass =  bcrypt_context.hash(user.password)
        add_user = Users(
        name = user.name,
        username = user.username,
        email = user.email,
        hashed_password = hashed_pass,
        role = user.role
        )
        db.add(add_user)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

    return "User Added Succesfully"

def authenticate_user(username,password,db) -> bool :
    try:
        user = db.query(Users).filter(Users.username == username).first()
        if not user:
            return False
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
        user = db.query(Users).filter(Users.username == username).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")
    
    JWT_payload = {
        "sub": str(datetime.utcnow()),
        "name": user.name,
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
async def login_for_token(
    form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
    db:DbDependency
):
    is_authenticated = authenticate_user(form_data.username,form_data.password,db)
    if not is_authenticated:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return create_JWT(form_data.username, db)