from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models.User import User
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from utils.db_session import get_db
from passlib.context import CryptContext

DbDependency = Annotated[Session,Depends(get_db)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def authenticate_user(username, password, db: DbDependency):
    try:
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return False

        is_verified = bcrypt_context.verify(password,user.hashed_password)
        if not is_verified:
            return False
            
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB Error {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error: {e}") 
    return True