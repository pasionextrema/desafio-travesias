from fastapi import APIRouter

from app.core.database import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    db_ok = await check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "version": "0.1.0",
    }


@router.get("/health/ping")
async def ping():
    return {"ping": "pong"}
