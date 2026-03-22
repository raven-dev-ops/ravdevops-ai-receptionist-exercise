from __future__ import annotations

import json
import logging
from typing import Any
import uuid

from fastapi import Request


REQUEST_ID_HEADER = "X-Request-ID"
logger = logging.getLogger("ravdevops_ai_receptionist.request")


def assign_request_id(request: Request) -> str:
    incoming = request.headers.get(REQUEST_ID_HEADER, "").strip()
    request_id = incoming[:64] if incoming else uuid.uuid4().hex
    request.state.request_id = request_id
    return request_id


def get_request_id(request: Request) -> str:
    request_id = getattr(request.state, "request_id", "")
    return str(request_id) if request_id else assign_request_id(request)


def log_request_event(event: str, request_id: str, **fields: Any) -> None:
    payload = {"event": event, "request_id": request_id, **fields}
    logger.info(json.dumps(payload, sort_keys=True, default=str))
