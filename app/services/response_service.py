from __future__ import annotations

from app.services.rag_service import RetrievedChunk
from app.services.scheduler_service import SchedulingDecision


def build_response(message: str, retrieved: list[RetrievedChunk], scheduling: SchedulingDecision) -> str:
    parts: list[str] = []

    if retrieved:
        context_summary = " ".join(item.text for item in retrieved[:2])
        parts.append(f"Based on the current knowledge base: {context_summary}")
    else:
        parts.append(
            "I don't have that information in the current knowledge base. "
            "I can route this for manual follow-up instead of guessing."
        )

    if scheduling.status == "scheduled":
        parts.append(
            f"I noted your requested follow-up time ({scheduling.requested_time_text}) and normalized it for follow-up."
        )
    elif scheduling.status == "outside_business_hours":
        parts.append(
            "I captured your requested follow-up time, but it falls outside business hours, so it needs manual review."
        )
    elif scheduling.status == "ambiguous_time":
        parts.append(
            "I captured the follow-up request, but the time reference is ambiguous and needs manual confirmation."
        )
    elif scheduling.status == "manual_follow_up":
        parts.append(
            "I captured the follow-up request, but the time needs manual confirmation before it can be booked."
        )

    return " ".join(parts)
