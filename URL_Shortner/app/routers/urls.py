from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from schemas.url_create import URLCreate
from starlette import status
from models.URL import Url
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import timedelta, timezone, datetime
from utils.alias import generate_short_code
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from utils.db_session import get_db
from schemas.url_response import URLResponse
from models.User import User
from utils.authenticate import authenticate_user

security = HTTPBasic()
credentials = Annotated[HTTPBasicCredentials, Depends(security)]
router = APIRouter(prefix="/url", tags=["url"])
DbDependency = Annotated[Session, Depends(get_db)]


def get_response(db: DbDependency, alias):
    data = db.query(Url).filter(Url.urlCode == alias).first()
    return {
        "short_code": data.urlCode,
        "short_url": f"http://localhost:8000/url/{data.urlCode}",
        "original_url": data.original_url,
        "created_at": data.created_at,
        "expires_at": data.expires_at,
    }


# Create Short_url
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=URLResponse)
def shorten_url(payload: URLCreate, db: DbDependency, cred: credentials):
    try:
        user = authenticate_user(cred.username, cred.password, db)
        get_user_data = db.query(User).filter(User.username == cred.username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not Validate User",
                headers={"WWW-Authenticate": "Basic"},
            )

        if get_user_data.role == "Admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin can not create URLs",
            )

        if get_user_data.subscription_type == "Basic":
            expired_minutes = timedelta(minutes=7)  # should use days=

        elif get_user_data.subscription_type == "Premium":
            if payload.expires_in is None:
                expired_minutes = timedelta(minutes=70)
            else:
                expired_minutes = timedelta(minutes=payload.expires_in)

        if payload.urlCode:
            alias = payload.urlCode

        else:
            alias = generate_short_code()

        data = Url(
            original_url=str(payload.original_url),
            urlCode=alias,
            expires_at=datetime.now(timezone.utc) + expired_minutes,
            user_id=get_user_data.id,
        )

        db.add(data)
        db.commit()
        db.refresh(data)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Alias already taken"
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {e}"
        )

    return get_response(db, alias)


# Get All Url by Username
@router.get("/")
def get_all_urls_by_username(db: DbDependency, cred: credentials):
    user = authenticate_user(cred.username, cred.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not Validate User",
            headers={"WWW-Authenticate": "Basic"},
        )

    user_data = db.query(User).filter(User.username == cred.username).first()
    user_id = user_data.id
    url_data = db.query(Url).filter(Url.user_id == user_id).all()

    return url_data


# Get Url by Alias/Short Code of logged in username
@router.get("/{alias}")
def get_url(
    db: DbDependency, cred: credentials, alias: str = Path(min_length=7, max_length=7)
):
    user = authenticate_user(cred.username, cred.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not Validate User",
            headers={"WWW-Authenticate": "Basic"},
        )

    get_id = db.query(User).filter(User.username == cred.username).first()
    data = db.query(Url).filter(Url.user_id == get_id.id, Url.urlCode == alias).first()
    if data is None:
        return "No Alias Present"

    if data.expired:
        return "URL Expired"

    return data


# Get Url by Alias/Short Code
@router.patch("/upgrade/{alias}")
def upgrade_expiry_for_url(
    db: DbDependency, cred: credentials, alias: str = Path(min_length=7, max_length=7)
):

    user = authenticate_user(cred.username, cred.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not Validate User",
            headers={"WWW-Authenticate": "Basic"},
        )

    get_id = db.query(User).filter(User.username == cred.username).first()
    data = db.query(Url).filter(Url.user_id == get_id.id, Url.urlCode == alias).first()

    if not get_id.subscription_type == "Premium":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Basic User can't upgrade the URL",
        )

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Code doesn't Exist"
        )

    current_date = datetime.now(timezone.utc)

    if current_date > data.expires_at:
        if get_id.subscription_type == "Basic":
            data.expired = True

            db.commit()
            db.refresh(data)

            return {
                "status": "URL is Expired and cannot be used, Upgrade Membership to Update Expiry_date and Alias"
            }

        data.expires_at = current_date + timedelta(minutes=50)
        data.urlCode = generate_short_code()

        db.commit()
        db.refresh(data)

        return {
            "status": "URL was Expired. Alias and Expiry Time has now been updated as part of your Premier Membership",
            "New Alias": data.urlCode,
            "Now Expired At": data.expires_at,
        }

    else:
        return {"status": "URL Not expired Yet", "Expired At": data.expires_at}


# For a modern URL shortener, if Expired:
# Do this:
# mark expired
# block redirects
# preserve alias reservation
# allow owner to:
# extend expiry
# duplicate link into new alias
# permanently delete
# Avoid:
# immediate hard deletion
# instant alias reuse
# because reused aliases can become a security and trust problem.
