from DB.models import Users
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from fastapi import APIRouter, Path, Query, HTTPException, Depends
from schemas import TodoCreate
from DB.models import Todos

from DB.db import SessionLocal

router = APIRouter()

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

@router.post("/user")
def create_user():
    