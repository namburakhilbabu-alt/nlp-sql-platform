from fastapi import APIRouter
from datetime import datetime
from app.core.config import settings
from app.models.database import execute_query

router = APIRouter()


@router.get("/health")
def health_check():
    db_ok = False
    try:
        execute_query("SELECT 1")
        db_ok = True
    except Exception:
        pass

    return {
        "status": "healthy" if db_ok else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "app": settings.app_name,
        "version": settings.app_version,
        "database": "connected" if db_ok else "error",
        "environment": settings.app_env,
    }
