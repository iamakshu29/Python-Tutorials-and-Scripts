from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from utils.logger import log_event
import logging

# DB lifecycle and DB Session Depends on it
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        log_event(logging.ERROR,"Data Rolled Back")
        raise HTTPException(status_code=500,detail=f"DB commit failed: {e}")
    finally:
        db.close()

# Move this to dependencies.py