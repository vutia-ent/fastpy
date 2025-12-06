"""
Health check endpoints for monitoring.
"""
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import text

from app.config.settings import settings
from app.database.connection import get_session

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns the service status.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/ready")
async def readiness_check(session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
    """
    Readiness check endpoint.
    Verifies database connectivity.
    """
    checks = {
        "database": False,
    }

    # Check database
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass

    all_healthy = all(checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint.
    Simple check that the service is running.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/info")
async def service_info() -> Dict[str, Any]:
    """
    Service information endpoint.
    Returns detailed information about the service.

    Note: This endpoint is disabled in production to prevent information disclosure.
    """
    # Restrict access in production to prevent information disclosure
    if settings.is_production:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "environment": settings.environment,
        "debug": settings.debug,
        "database_driver": settings.db_driver,
        "features": {
            "rate_limiting": settings.rate_limit_enabled,
            "email": settings.mail_enabled,
            "caching": settings.cache_enabled,
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
