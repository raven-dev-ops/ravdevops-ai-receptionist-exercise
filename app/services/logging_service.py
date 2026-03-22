from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.db_models import Appointment, CallLog
from app.services.rag_service import RetrievedChunk
from app.services.scheduler_service import SchedulingDecision


def create_call_log(
    db: Session,
    request_id: str,
    caller_id: str,
    message: str,
    ai_response: str,
    retrieved: list[RetrievedChunk],
) -> CallLog:
    joined_context = "\n---\n".join(item.text for item in retrieved)
    top_score = retrieved[0].score if retrieved else 0.0
    row = CallLog(
        request_id=request_id,
        caller_id=caller_id,
        message=message,
        ai_response=ai_response,
        retrieved_context=joined_context,
        retrieval_score=top_score,
        retrieval_diagnostics=[item.to_diagnostic() for item in retrieved],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_appointment(
    db: Session,
    request_id: str,
    caller_id: str,
    scheduling: SchedulingDecision,
) -> Appointment:
    row = Appointment(
        request_id=request_id,
        caller_id=caller_id,
        requested_time_text=scheduling.requested_time_text or "unspecified",
        normalized_time=scheduling.normalized_time or "",
        normalized_time_local=scheduling.normalized_time_local or "",
        timezone=scheduling.timezone or "",
        status=scheduling.status,
        notes=scheduling.notes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
