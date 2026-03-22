import base64
import hashlib
import hmac
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path("./data/test_exercise.db")
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = "sqlite:///./data/test_exercise.db"
os.environ["SCHEDULER_NOW_OVERRIDE"] = "2026-03-20T09:00:00-05:00"


def _load_app():
    from app.main import app  # noqa: WPS433
    return app


@pytest.fixture(scope="session")
def client() -> TestClient:
    app = _load_app()
    return TestClient(app)


def _json(response) -> Any:
    assert response.headers.get("content-type", "").startswith("application/json")
    return response.json()


def _twilio_signature(url: str, params: dict[str, str], auth_token: str) -> str:
    payload = url + "".join(f"{key}{params[key]}" for key in sorted(params))
    digest = hmac.new(auth_token.encode("utf-8"), payload.encode("utf-8"), hashlib.sha1).digest()
    return base64.b64encode(digest).decode("utf-8")


def _set_setting(name: str, value: str) -> str:
    from app.config import settings  # noqa: WPS433

    previous = getattr(settings, name)
    object.__setattr__(settings, name, value)
    return previous


def test_health_endpoint_exists(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = _json(response)
    assert isinstance(data, dict)
    assert data["status"] in {"ok", "healthy", "ready"}
    assert data["ready"] is True
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["knowledge_base"] == "ok"


def test_readyz_endpoint_exists(client: TestClient) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    data = _json(response)
    assert data["status"] == "ready"
    assert data["ready"] is True


def test_incoming_call_accepts_valid_payload(client: TestClient) -> None:
    payload = {
        "caller_id": "+18165551212",
        "message": "Do you offer software engineering work and can someone call me tomorrow morning?",
    }
    response = client.post("/incoming-call", json=payload)
    assert response.status_code == 200
    data = _json(response)
    assert "response_text" in data
    assert data["response_text"].strip() != ""
    assert "call_id" in data
    assert "request_id" in data
    assert response.headers["X-Request-ID"] == data["request_id"]
    assert data["scheduling_status"] == "ambiguous_time"
    assert isinstance(data["retrieval_diagnostics"], list)
    assert data["retrieval_diagnostics"]


def test_incoming_call_rejects_invalid_payload(client: TestClient) -> None:
    payload = {"caller_id": ""}
    response = client.post("/incoming-call", json=payload)
    assert response.status_code in {400, 422}


def test_logs_endpoint_returns_collection(client: TestClient) -> None:
    seed_payload = {
        "caller_id": "+18165550001",
        "message": "What are your business hours?",
    }
    seed_response = client.post("/incoming-call", json=seed_payload)
    assert seed_response.status_code == 200

    response = client.get("/logs")
    assert response.status_code == 200
    data = _json(response)
    assert isinstance(data, list)
    if data:
        first = data[0]
        assert "request_id" in first
        assert any(key in first for key in ["caller_id", "phone_number"])
        assert any(key in first for key in ["message", "user_message"])
        assert any(key in first for key in ["ai_response", "response_text"])
        assert "retrieval_diagnostics" in first
        assert isinstance(first["retrieval_diagnostics"], list)


def test_appointments_endpoint_returns_collection(client: TestClient) -> None:
    payload = {
        "caller_id": "+18165550002",
        "message": "Please schedule me for tomorrow at 10 AM.",
    }
    seed_response = client.post("/incoming-call", json=payload)
    assert seed_response.status_code == 200

    response = client.get("/appointments")
    assert response.status_code == 200
    data = _json(response)
    assert isinstance(data, list)
    if data:
        first = data[0]
        assert "request_id" in first
        assert any(key in first for key in ["caller_id", "phone_number"])
        assert any(
            key in first
            for key in ["requested_time_text", "requested_time", "normalized_time", "appointment_time"]
        )
        assert first["normalized_time"].endswith("+00:00")
        assert first["normalized_time_local"].endswith("-05:00")
        assert first["timezone"] == "America/Chicago"


def test_unknown_information_is_not_hallucinated(client: TestClient) -> None:
    payload = {
        "caller_id": "+18165550003",
        "message": "What is your platinum emergency moonlight irrigation package price?",
    }
    response = client.post("/incoming-call", json=payload)
    assert response.status_code == 200
    data = _json(response)
    text = data["response_text"].lower()

    acceptable_signals = [
        "don't have",
        "do not have",
        "not available",
        "not in the knowledge base",
        "unable to find",
        "i can route this for manual follow-up",
        "information unavailable",
    ]
    assert any(signal in text for signal in acceptable_signals)


def test_scheduling_outside_business_rules_is_not_blindly_confirmed(client: TestClient) -> None:
    payload = {
        "caller_id": "+18165550004",
        "message": "Book me for 3:00 AM tomorrow.",
    }
    response = client.post("/incoming-call", json=payload)
    assert response.status_code == 200
    data = _json(response)
    text = data["response_text"].lower()

    forbidden_phrases = [
        "confirmed for 3:00 am",
        "booked for 3:00 am",
        "scheduled for 3:00 am",
    ]
    assert not any(phrase in text for phrase in forbidden_phrases)
    assert data["scheduling_status"] == "outside_business_hours"


def test_docs_or_openapi_available(client: TestClient) -> None:
    docs_response = client.get("/docs")
    openapi_response = client.get("/openapi.json")
    assert docs_response.status_code == 200 or openapi_response.status_code == 200


def test_request_id_round_trips_to_logs(client: TestClient) -> None:
    request_id = "req-integration-123"
    payload = {
        "caller_id": "+18165550005",
        "message": "What are your business hours and integration capabilities?",
    }
    response = client.post("/incoming-call", json=payload, headers={"X-Request-ID": request_id})
    assert response.status_code == 200
    body = _json(response)
    assert response.headers["X-Request-ID"] == request_id
    assert body["request_id"] == request_id

    logs_response = client.get("/logs")
    assert logs_response.status_code == 200
    logs = _json(logs_response)
    assert any(item["request_id"] == request_id for item in logs)


def test_ambiguous_time_requests_are_captured_for_manual_follow_up(client: TestClient) -> None:
    payload = {
        "caller_id": "+18165550006",
        "message": "Can someone call me tomorrow morning about backend API support?",
    }
    response = client.post("/incoming-call", json=payload)
    assert response.status_code == 200
    body = _json(response)

    assert body["scheduled"] is False
    assert body["scheduling_status"] == "ambiguous_time"
    assert "manual" in body["response_text"].lower() or "ambiguous" in body["response_text"].lower()
    assert body["appointment_id"] is not None

    appointments_response = client.get("/appointments")
    appointments = _json(appointments_response)
    appointment = next(item for item in appointments if item["id"] == body["appointment_id"])
    assert appointment["status"] == "ambiguous_time"
    assert appointment["normalized_time"] == ""
    assert appointment["timezone"] == "America/Chicago"


def test_retrieval_diagnostics_are_structured_for_supported_queries(client: TestClient) -> None:
    payload = {
        "caller_id": "+18165550007",
        "message": "Do you handle backend APIs, integration layers, and operational handoff?",
    }
    response = client.post("/incoming-call", json=payload)
    assert response.status_code == 200
    body = _json(response)

    diagnostics = body["retrieval_diagnostics"]
    assert diagnostics
    first = diagnostics[0]
    assert first["score"] > 0
    assert first["rank"] >= 1
    assert first["retrieval_method"] == "local_hashed_tfidf"
    assert isinstance(first["matched_terms"], list)
    assert first["excerpt"].strip() != ""


def test_twilio_adapter_accepts_unsigned_requests_in_local_mode(client: TestClient) -> None:
    payload = {"From": "+18165550008", "Body": "What are your business hours?"}
    response = client.post(
        "/twilio/incoming-call",
        content=urlencode(payload),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    body = _json(response)
    assert body["request_id"]
    assert "hours" in body["response_text"].lower()


def test_twilio_adapter_rejects_invalid_signature_when_enforced(client: TestClient) -> None:
    previous_mode = _set_setting("twilio_signature_validation", "required")
    previous_token = _set_setting("twilio_auth_token", "secret-token")
    try:
        payload = {"From": "+18165550009", "Body": "Call me tomorrow at 10 AM."}
        response = client.post(
            "/twilio/incoming-call",
            content=urlencode(payload),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Twilio-Signature": "invalid-signature",
            },
        )
        assert response.status_code == 403
        detail = _json(response)["detail"].lower()
        assert "signature" in detail
    finally:
        _set_setting("twilio_signature_validation", previous_mode)
        _set_setting("twilio_auth_token", previous_token)


def test_twilio_adapter_accepts_valid_signature_when_enforced(client: TestClient) -> None:
    previous_mode = _set_setting("twilio_signature_validation", "required")
    previous_token = _set_setting("twilio_auth_token", "secret-token")
    previous_base_url = _set_setting("twilio_webhook_base_url", "")
    try:
        payload = {"From": "+18165550010", "Body": "Can someone call me next monday at 10 AM?"}
        url = "http://testserver/twilio/incoming-call"
        signature = _twilio_signature(url, payload, "secret-token")
        response = client.post(
            "/twilio/incoming-call",
            content=urlencode(payload),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Twilio-Signature": signature,
            },
        )
        assert response.status_code == 200
        body = _json(response)
        assert body["scheduled"] is True
        assert body["scheduling_status"] == "scheduled"
    finally:
        _set_setting("twilio_signature_validation", previous_mode)
        _set_setting("twilio_auth_token", previous_token)
        _set_setting("twilio_webhook_base_url", previous_base_url)
