import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.settings import Settings
from dependencies.core import get_settings
from database.engine import get_db_session
from typing import Dict, Any

router = APIRouter()

@router.get("", response_model=Dict[str, Any])
async def health_check(
    settings: Settings = Depends(get_settings),
    db_session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Health check endpoint to verify service and database status."""
    
    db_status = {"status": "ok", "latency_ms": 0}
    start_time = time.time()
    
    try:
        await db_session.execute(text("SELECT 1"))
        db_status["latency_ms"] = round((time.time() - start_time) * 1000, 2)
    except Exception as e:
        db_status["status"] = "error"
        db_status["error"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "service": settings.app_name,
                "version": settings.app_version,
                "database": db_status
            }
        )
        
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "database": db_status
    }
