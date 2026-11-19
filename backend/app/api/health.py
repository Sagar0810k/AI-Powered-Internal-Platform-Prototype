from fastapi import APIRouter
from sqlalchemy import text

from app.database import SessionLocal

router = APIRouter()


@router.get("/health")
def health():
    """Liveness/readiness probe: app up + DB connectivity check."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        return {"status": "degraded", "detail": "database_unreachable"}
    return {"status": "ok"}
