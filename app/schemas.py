from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IncomingCallRequest(ORMModel):
    caller_id: str = Field(..., min_length=3, max_length=64)
    message: str = Field(..., min_length=3, max_length=5000)


class RetrievalDiagnostic(ORMModel):
    chunk_id: int
    score: float
    rank: int
    matched_terms: list[str] = Field(default_factory=list)
    retrieval_method: str
    excerpt: str


class IncomingCallResponse(ORMModel):
    call_id: int
    response_text: str
    scheduled: bool
    appointment_id: Optional[int] = None
    retrieved_context: list[str]
    request_id: str = ""
    scheduling_status: str = ""
    retrieval_diagnostics: list[RetrievalDiagnostic] = Field(default_factory=list)


class HealthResponse(ORMModel):
    status: str
    app: str
    ready: bool = True
    checks: dict[str, str] = Field(default_factory=dict)


class CallLogResponse(ORMModel):
    id: int
    request_id: str = ""
    caller_id: str
    message: str
    ai_response: str
    retrieved_context: str
    retrieval_score: float
    retrieval_diagnostics: list[RetrievalDiagnostic] = Field(default_factory=list)
    created_at: datetime


class AppointmentResponse(ORMModel):
    id: int
    request_id: str = ""
    caller_id: str
    requested_time_text: str
    normalized_time: str
    normalized_time_local: str = ""
    timezone: str = ""
    status: str
    notes: str
    created_at: datetime
