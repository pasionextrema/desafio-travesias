from fastapi import APIRouter

from app.core.database import check_db_connection
from app.core.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
async def health_check():
    db_ok = await check_db_connection()
    raw_url = settings._get_raw_db_url()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "db_configured": bool(raw_url),
        "db_url_prefix": raw_url.split("@")[-1].split("/")[0] if raw_url and "@" in raw_url else "unknown",
        "version": "0.1.0",
    }


@router.get("/health/ping")
async def ping():
    return {"ping": "pong"}
