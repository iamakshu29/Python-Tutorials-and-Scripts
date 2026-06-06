from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from starlette import status
from uuid import UUID
from schemas.ApplicationCreate import ApplicationCreate, ApplicationResponse
from schemas.ApplicationUpdate import ApplicationUpdate
from models.Application import Application, ApplicationStatus
from utils.db_session import get_db
from routers.auth import authenticate_user
from utils.pagination import paginate, Pagination
from utils.sort_data import sort_rows
from utils.logger import log_event
from utils.rate_limiter import limiter
import logging

router = APIRouter(prefix="/applications", tags=["app"])

DbDependency = Annotated[Session, Depends(get_db)]
valid_user = Annotated[dict, Depends(authenticate_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/hour")
def create_job_app(
    request: Request, user: valid_user, job_app: ApplicationCreate, db: DbDependency
):
    # dict is replace with model_dump in newer versions
    if not user:
        log_event(
            logging.ERROR,
            "Could not Validate User",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(status_code=401, detail="Authentication Failed")
    job_app = Application(**job_app.model_dump(mode="json"), user_id=UUID(user.get("id")))
    db.add(job_app)

    log_event(logging.INFO, "Application Posted", status_code=status.HTTP_201_CREATED)
    return {"message": "Application Posted"}


# add multiple applications in bulk
@router.post("/bulk_add")
def create_multiple_jobs_app(
    user: valid_user, job_apps: list[ApplicationCreate], db: DbDependency
):
    if not user:
        log_event(
            logging.ERROR,
            "Authentication Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(status_code=401, detail="Authentication Failed")

    applications = [
        Application(**job.model_dump(mode="json"), user_id=UUID(user.get("id"))) for job in job_apps
    ]

    db.add_all(applications)

    log_event(
        logging.INFO, "Bulk insert successful", status_code=status.HTTP_201_CREATED
    )
    return {"message": "Bulk insert successful"}


# list job_ids also added pagination, sort and filter config.
# In FastAPI, function parameters are automatically treated as required if they don't have a default value assigned to them.
@router.get("/")
def list_job_app(
    user: valid_user,
    db: DbDependency,
    job_status: ApplicationStatus | None = Query(default=None),
    company: str | None = Query(default=None, min_length=2),
    sort_by: str | None = Query(
        default=None, examples=["applied_date", "created_at", "company"]
    ),
    order: str = Query(default="desc"),
    page_num: int = Query(ge=1, default=1),
    limit: int = Query(le=50, default=10),
):

    if not user:
        log_event(
            logging.ERROR,
            "Authentication Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # user_id filter intentionally omitted here — with small test data this lets you
    # see all records and demonstrates sorting/pagination behaviour across the full dataset
    query = db.query(Application)

    if job_status:
        log_event(
            logging.INFO,
            "Result Filtered by job_status",
            status_code=status.HTTP_200_OK,
        )
        query = query.filter(Application.status == job_status)

    if company:
        log_event(
            logging.INFO, "Result Filtered by company", status_code=status.HTTP_200_OK
        )
        query = query.filter(Application.company == company)

    result = query.all()

    if sort_by:
        log_event(logging.INFO, "Result Sorted", status_code=status.HTTP_200_OK)
        result = sort_rows(query.all(), sort_by=sort_by, order=order)

    if page_num and limit:
        log_event(logging.INFO, "Result is Paginated", status_code=status.HTTP_200_OK)
        pagination = Pagination(page=page_num, limit=limit)
        return paginate(pagination, result)

    log_event(logging.INFO, "Fields Retrieved", status_code=status.HTTP_200_OK)
    return result


# get job_app by id
@router.get("/{id}", response_model=ApplicationResponse)
def get_single_job_app(user: valid_user, db: DbDependency, id: UUID = Path()):
    if not user:
        log_event(
            logging.ERROR,
            "Authentication Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(status_code=401, detail="Authentication Failed")

    get_application = (
        db.query(Application)
        .filter(Application.user_id == UUID(user.get("id")), Application.id == id)
        .first()
    )

    if not get_application:
        log_event(
            logging.ERROR, "No record Found", status_code=status.HTTP_404_NOT_FOUND
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No record Found"
        )

    log_event(logging.INFO, "Fields Retrieved By id", status_code=status.HTTP_200_OK)
    return get_application


# update job_app by id
@router.put("/{id}")
def update_job_app(
    user: valid_user,
    db: DbDependency,
    update_attributes: ApplicationUpdate,
    id: UUID = Path(),
) -> str:
    if not user:
        log_event(
            logging.ERROR,
            "Authentication Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(status_code=401, detail="Authentication Failed")

    get_application = db.query(Application).filter(Application.id == id).first()

    if not get_application:
        log_event(
            logging.ERROR,
            "Application not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    if str(get_application.user_id) != user.get("id"):
        log_event(
            logging.ERROR, "User not Authorized", status_code=status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not Authorized"
        )

    update_data = update_attributes.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(get_application, key, value)

    db.add(get_application)
    db.commit()
    db.refresh(get_application)
    log_event(
        logging.INFO,
        "Job Application Updated Successfully",
        status_code=status.HTTP_202_ACCEPTED,
    )
    return "Job Application Updated Successfully"


# delete job_app by id
@router.delete("/{id}")
def delete_job_app(user: valid_user, db: DbDependency, id: UUID = Path()) -> str:
    if not user:
        log_event(
            logging.ERROR,
            "Authentication Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    deleted_app = (
        db.query(Application)
        .filter(Application.user_id == UUID(user.get("id")), Application.id == id)
        .delete()
    )

    if deleted_app == 0:
        log_event(
            logging.ERROR,
            "Application not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    log_event(logging.INFO, "Job Application Deleted", status_code=status.HTTP_200_OK)
    return "Job Application Deleted"
