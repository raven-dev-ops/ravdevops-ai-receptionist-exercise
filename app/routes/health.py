from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas import HealthResponse
from app.services.health_service import collect_health_status

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    summary = collect_health_status()
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        ready=summary.ready,
        checks=summary.checks,
    )


@router.get("/readyz", response_model=HealthResponse)
def readyz() -> HealthResponse:
    summary = collect_health_status()
    response = HealthResponse(
        status=summary.status,
        app=settings.app_name,
        ready=summary.ready,
        checks=summary.checks,
    )
    if summary.ready:
        return response
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=response.model_dump(),
    )
