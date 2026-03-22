from __future__ import annotations

from fastapi import FastAPI, Request

from app.config import settings
from app.db import init_db
from app.routes.appointments import router as appointments_router
from app.routes.calls import router as calls_router
from app.routes.health import router as health_router
from app.routes.logs import router as logs_router
from app.routes.twilio import router as twilio_router
from app.services.observability_service import REQUEST_ID_HEADER, assign_request_id, log_request_event

init_db()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Public RavDevOps candidate exercise for AI systems, retrieval, "
        "scheduling, and containerized backend delivery."
    ),
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = assign_request_id(request)
    log_request_event("request_started", request_id, method=request.method, path=request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        log_request_event("request_failed", request_id, method=request.method, path=request.url.path)
        raise

    response.headers[REQUEST_ID_HEADER] = request_id
    log_request_event(
        "request_completed",
        request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response


app.include_router(health_router)
app.include_router(calls_router)
app.include_router(logs_router)
app.include_router(appointments_router)
app.include_router(twilio_router)
