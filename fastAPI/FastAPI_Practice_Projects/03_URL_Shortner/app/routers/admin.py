from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from utils.db_session import get_db
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from utils.authenticate import authenticate_user
from schemas.user_response import UserResponse
from schemas.url_response import BulkURLResponse
from models.User import User
from models.URL import Url
from starlette import status

router = APIRouter(prefix="/admin", tags=["admin"])

DbDependency = Annotated[Session, Depends(get_db)]
security = HTTPBasic()
credentials = Annotated[HTTPBasicCredentials, Depends(security)]


# Get all User Details - Admin Only
@router.get("/user", response_model=list[UserResponse])
def get_all_user_details(db: DbDependency, cred: credentials):
    try:
        user = authenticate_user(cred.username, cred.password, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not Validate User",
                headers={"WWW-Authenticate": "Basic"},
            )

        data = db.query(User).filter(User.username == cred.username).first()

        if data.role != "Admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not Validate User",
            )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB Error {e}"
        )

    return db.query(User).all()


# Get All Url - Admin Only
@router.get("/url", response_model=list[BulkURLResponse])
def get_all_urls_by(db: DbDependency, cred: credentials):
    user = authenticate_user(cred.username, cred.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not Validate User",
        )

    data = db.query(User).filter(User.username == cred.username).first()

    if data.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not Validate User",
        )

    url_data = db.query(Url).all()

    return url_data


# Delete Url by Alias/Short_code - Admin Only
@router.delete("/urls/{alias}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(
    db: DbDependency, cred: credentials, alias=Path(min_length=7, max_length=7)
):
    try:
        user = authenticate_user(cred.username, cred.password, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not Validate User",
                headers={"WWW-Authenticate": "Basic"},
            )

        data = db.query(User).filter(User.username == cred.username).first()

        if data.role != "Admin":
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not Validate User",
        )

        get_alias = db.query(Url).filter(Url.urlCode == alias).delete()

        if get_alias == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not Found"
            )

        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {e}"
        )

    return "Deleted"
