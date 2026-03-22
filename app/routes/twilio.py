from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import IncomingCallResponse
from app.services.call_flow_service import process_incoming_call
from app.services.observability_service import get_request_id
from app.services.twilio_service import (
    parse_twilio_form,
    require_valid_twilio_request,
    twilio_form_to_incoming_call,
)

router = APIRouter(prefix="/twilio", tags=["twilio"])


@router.post("/incoming-call", response_model=IncomingCallResponse)
async def twilio_incoming_call(request: Request, db: Session = Depends(get_db)) -> IncomingCallResponse:
    request_id = get_request_id(request)
    body = await request.body()
    form_fields = parse_twilio_form(body)
    require_valid_twilio_request(request, form_fields)
    payload = twilio_form_to_incoming_call(form_fields)
    response = process_incoming_call(payload=payload, request_id=request_id, db=db)
    return response
