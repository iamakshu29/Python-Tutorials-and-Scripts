from fastapi import APIRouter

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/")
def get_status_in_prometheus_format():
    return None
