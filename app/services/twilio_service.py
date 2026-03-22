from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import hmac
from typing import Any
from urllib.parse import parse_qs

from fastapi import HTTPException, Request, status
from pydantic import ValidationError

from app.config import settings
from app.schemas import IncomingCallRequest


TWILIO_SIGNATURE_HEADER = "X-Twilio-Signature"
VALIDATION_DISABLED = "disabled"
VALIDATION_IF_CONFIGURED = "if_configured"
VALIDATION_REQUIRED = "required"


@dataclass(frozen=True)
class TwilioValidationResult:
    enforced: bool
    valid: bool
    reason: str = ""


def _normalized_validation_mode() -> str:
    mode = settings.twilio_signature_validation.strip().lower()
    if mode in {VALIDATION_DISABLED, VALIDATION_IF_CONFIGURED, VALIDATION_REQUIRED}:
        return mode
    return VALIDATION_IF_CONFIGURED


def _validation_is_enforced() -> bool:
    mode = _normalized_validation_mode()
    if mode == VALIDATION_DISABLED:
        return False
    if mode == VALIDATION_REQUIRED:
        return True
    return bool(settings.twilio_auth_token.strip())


def parse_twilio_form(body: bytes) -> dict[str, str]:
    parsed = parse_qs(body.decode("utf-8"), keep_blank_values=True)
    return {key: values[0] if values else "" for key, values in parsed.items()}


def _request_url_for_signature(request: Request) -> str:
    if settings.twilio_webhook_base_url.strip():
        base = settings.twilio_webhook_base_url.strip().rstrip("/")
        query = f"?{request.url.query}" if request.url.query else ""
        return f"{base}{request.url.path}{query}"
    return str(request.url)


def compute_twilio_signature(url: str, params: dict[str, str], auth_token: str) -> str:
    payload = url + "".join(f"{key}{params[key]}" for key in sorted(params))
    digest = hmac.new(auth_token.encode("utf-8"), payload.encode("utf-8"), hashlib.sha1).digest()
    return base64.b64encode(digest).decode("utf-8")


def validate_twilio_request(request: Request, params: dict[str, str]) -> TwilioValidationResult:
    if not _validation_is_enforced():
        return TwilioValidationResult(enforced=False, valid=True)

    auth_token = settings.twilio_auth_token.strip()
    if not auth_token:
        return TwilioValidationResult(
            enforced=True,
            valid=False,
            reason="Twilio signature validation is enforced but TWILIO_AUTH_TOKEN is not configured.",
        )

    provided_signature = request.headers.get(TWILIO_SIGNATURE_HEADER, "").strip()
    if not provided_signature:
        return TwilioValidationResult(
            enforced=True,
            valid=False,
            reason="Missing X-Twilio-Signature header.",
        )

    expected_signature = compute_twilio_signature(
        url=_request_url_for_signature(request),
        params=params,
        auth_token=auth_token,
    )
    is_valid = hmac.compare_digest(provided_signature, expected_signature)
    if is_valid:
        return TwilioValidationResult(enforced=True, valid=True)

    return TwilioValidationResult(
        enforced=True,
        valid=False,
        reason="Twilio signature validation failed.",
    )


def require_valid_twilio_request(request: Request, params: dict[str, str]) -> None:
    result = validate_twilio_request(request, params)
    if result.valid:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=result.reason)


def twilio_form_to_incoming_call(params: dict[str, Any]) -> IncomingCallRequest:
    try:
        return IncomingCallRequest(
            caller_id=str(params.get("From", "")).strip(),
            message=str(params.get("Body", "")).strip(),
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc
