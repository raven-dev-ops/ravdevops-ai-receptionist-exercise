from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import IncomingCallRequest, IncomingCallResponse
from app.services.call_flow_service import process_incoming_call
from app.services.observability_service import get_request_id

router = APIRouter(prefix="", tags=["calls"])


@router.post("/incoming-call", response_model=IncomingCallResponse)
def incoming_call(
    payload: IncomingCallRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> IncomingCallResponse:
    request_id = get_request_id(request)
    return process_incoming_call(payload=payload, request_id=request_id, db=db)
