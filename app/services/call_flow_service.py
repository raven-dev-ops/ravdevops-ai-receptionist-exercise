from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import settings
from app.schemas import IncomingCallRequest, IncomingCallResponse
from app.services.kb_service import load_chunks
from app.services.logging_service import create_appointment, create_call_log
from app.services.rag_service import retrieve_context
from app.services.response_service import build_response
from app.services.scheduler_service import analyze_scheduling_request


def process_incoming_call(
    payload: IncomingCallRequest,
    request_id: str,
    db: Session,
) -> IncomingCallResponse:
    chunks = load_chunks(settings.knowledge_base_path)
    retrieved = retrieve_context(payload.message, chunks)
    scheduling = analyze_scheduling_request(payload.message)
    response_text = build_response(payload.message, retrieved, scheduling)

    call = create_call_log(
        db=db,
        request_id=request_id,
        caller_id=payload.caller_id,
        message=payload.message,
        ai_response=response_text,
        retrieved=retrieved,
    )

    appointment_id = None
    if scheduling.should_create_appointment:
        appointment = create_appointment(
            db=db,
            request_id=request_id,
            caller_id=payload.caller_id,
            scheduling=scheduling,
        )
        appointment_id = appointment.id

    return IncomingCallResponse(
        call_id=call.id,
        response_text=response_text,
        scheduled=scheduling.status == "scheduled",
        appointment_id=appointment_id,
        retrieved_context=[item.text for item in retrieved],
        request_id=request_id,
        scheduling_status=scheduling.status,
        retrieval_diagnostics=[item.to_diagnostic() for item in retrieved],
    )
