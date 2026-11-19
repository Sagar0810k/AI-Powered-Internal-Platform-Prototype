from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app import models
from app.database import SessionLocal
from app.middleware import TOTAL_REQUESTS

router = APIRouter()


@router.get("/metrics")
def metrics() -> Response:
    """Prometheus scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/stats")
def stats() -> dict:
    """Simple metrics summary for the UI: total requests served + approvals executed."""
    db = SessionLocal()
    try:
        total_requests = TOTAL_REQUESTS["count"]
        approved_count = db.query(models.ApprovalRequest).filter(models.ApprovalRequest.status == "EXECUTED").count()
    finally:
        db.close()
    return {"total_requests": total_requests, "approved_count": approved_count}
