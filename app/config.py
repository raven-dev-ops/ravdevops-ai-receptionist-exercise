from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "RavDevOps AI Receptionist Exercise")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/exercise.db")
    knowledge_base_path: str = os.getenv("KNOWLEDGE_BASE_PATH", "./data/knowledge_base.txt")
    business_timezone: str = os.getenv("BUSINESS_TIMEZONE", "America/Chicago")
    business_open_hour: int = int(os.getenv("BUSINESS_OPEN_HOUR", "8"))
    business_close_hour: int = int(os.getenv("BUSINESS_CLOSE_HOUR", "18"))
    scheduler_now_override: str = os.getenv("SCHEDULER_NOW_OVERRIDE", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_signature_validation: str = os.getenv("TWILIO_SIGNATURE_VALIDATION", "if_configured")
    twilio_webhook_base_url: str = os.getenv("TWILIO_WEBHOOK_BASE_URL", "")


settings = Settings()
