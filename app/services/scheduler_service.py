from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.config import settings

TIME_RE = re.compile(r"(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<ampm>am|pm)", re.IGNORECASE)
WEEKDAY_NAMES = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
AMBIGUOUS_TIME_HINTS = ("morning", "afternoon", "evening", "later", "sometime")


@dataclass(frozen=True)
class SchedulingDecision:
    requested_time_text: str = ""
    normalized_time: str = ""
    normalized_time_local: str = ""
    timezone: str = ""
    status: str = "not_requested"
    notes: str = ""
    should_create_appointment: bool = False


def _business_timezone() -> ZoneInfo:
    try:
        return ZoneInfo(settings.business_timezone)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def _reference_time() -> datetime:
    tz = _business_timezone()
    if settings.scheduler_now_override:
        override = datetime.fromisoformat(settings.scheduler_now_override)
        if override.tzinfo is None:
            return override.replace(tzinfo=tz)
        return override.astimezone(tz)
    return datetime.now(tz)


def _resolve_requested_date(lowered_message: str, base: datetime) -> datetime:
    if "tomorrow" in lowered_message:
        return base + timedelta(days=1)

    for weekday_name, weekday_number in WEEKDAY_NAMES.items():
        if weekday_name not in lowered_message:
            continue
        offset = (weekday_number - base.weekday()) % 7
        if offset == 0:
            offset = 7
        return base + timedelta(days=offset)

    return base


def _parse_requested_time(message: str) -> tuple[str, datetime | None]:
    match = TIME_RE.search(message)
    if not match:
        return "", None

    hour = int(match.group("hour"))
    minute = int(match.group("minute") or "0")
    ampm = match.group("ampm").lower()

    if hour < 1 or hour > 12:
        return match.group(0), None

    if ampm == "pm" and hour != 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0

    base = _resolve_requested_date(message.lower(), _reference_time())
    normalized = base.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return match.group(0), normalized


def analyze_scheduling_request(message: str) -> SchedulingDecision:
    lowered = message.lower()
    wants_schedule = any(phrase in lowered for phrase in ["schedule", "book", "call me", "follow up", "follow-up"])
    if not wants_schedule:
        return SchedulingDecision()

    ambiguous_hint = next((hint for hint in AMBIGUOUS_TIME_HINTS if hint in lowered), "")
    requested_text, normalized = _parse_requested_time(message)
    timezone_name = _business_timezone().key

    if ambiguous_hint and normalized is None:
        return SchedulingDecision(
            requested_time_text=ambiguous_hint,
            timezone=timezone_name,
            status="ambiguous_time",
            notes="Scheduling was requested with an ambiguous time reference that needs manual confirmation.",
            should_create_appointment=True,
        )

    if normalized is None:
        return SchedulingDecision(
            requested_time_text=requested_text or "unspecified",
            timezone=timezone_name,
            status="manual_follow_up",
            notes="Scheduling was requested, but the requested time could not be normalized.",
            should_create_appointment=True,
        )

    reference_time = _reference_time()
    if normalized <= reference_time:
        return SchedulingDecision(
            requested_time_text=requested_text,
            normalized_time=normalized.astimezone(UTC).isoformat(),
            normalized_time_local=normalized.isoformat(),
            timezone=timezone_name,
            status="manual_follow_up",
            notes="Requested time is not in the future for the configured business timezone.",
            should_create_appointment=True,
        )

    if normalized.hour < settings.business_open_hour or normalized.hour >= settings.business_close_hour:
        return SchedulingDecision(
            requested_time_text=requested_text,
            normalized_time=normalized.astimezone(UTC).isoformat(),
            normalized_time_local=normalized.isoformat(),
            timezone=timezone_name,
            status="outside_business_hours",
            notes="Requested time falls outside configured business hours.",
            should_create_appointment=True,
        )

    return SchedulingDecision(
        requested_time_text=requested_text,
        normalized_time=normalized.astimezone(UTC).isoformat(),
        normalized_time_local=normalized.isoformat(),
        timezone=timezone_name,
        status="scheduled",
        notes="Requested time was normalized in the configured business timezone and stored in UTC.",
        should_create_appointment=True,
    )
