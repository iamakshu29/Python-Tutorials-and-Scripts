from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal

# DB lifecycle and DB Session Depends on it
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"DB commit failed: {e}")
    finally:
        db.close()

# Authenticate User by decoding the Token and match it with Payload values with Registered Users.
def authenticate_user(db: DbDependency, token: get_token) -> dict:
    payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

    if payload:
        payload_email: str = payload.get("email")
        payload_id: str = payload.get("id")
        payload_role: str = payload.get("role")
        db.query(User).filter(User.email == payload_email)
        return {"email":payload_email,"id":payload_id,"role":payload_role}
    raise JWTError