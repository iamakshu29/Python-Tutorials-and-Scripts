from requests import request
from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session
from dependencies import get_db
from models.service import Service
from models.health_check import HealthCheck

DbDependency = Annotated[Session, Depends(get_db)]


def query_service(service_name, db):
    return db.query(Service).filter(Service.name == service_name).first()


def is_healthy(service_name, db: DbDependency):
    service = query_service(service_name, db)
    response = request.get(service.health_url)

    duration_seconds = response.elapsed.total_seconds()
    duration_ms = round(duration_seconds * 1000, 2)

    service_status = ""
    error = ""
    if response.status_code == 200:
        service_status = "Healthy"
        error = "No Error"
    else:
        service_status = "Unhealthy"
        error = response.raise_for_status()

    health_check = HealthCheck(
        service_id=service.id,
        status=service_status,
        response_time_ms=duration_ms,
        status_code=response.status_code,
        error_detail=error,
    )
    db.add(health_check)
    db.commit()

    if service.current_status == service_status:
        return f"Status is same as before: {service_status}"
    else:
        return f"Status is Changed to {service_status}"
