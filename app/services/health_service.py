from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import text

from app.config import settings
from app.db import SessionLocal
from app.services.kb_service import load_chunks


@dataclass(frozen=True)
class HealthStatus:
    status: str
    checks: dict[str, str]

    @property
    def ready(self) -> bool:
        return self.status == "ready"


def collect_health_status() -> HealthStatus:
    checks: dict[str, str] = {}

    knowledge_base_path = Path(settings.knowledge_base_path)
    if not knowledge_base_path.exists():
        checks["knowledge_base"] = "missing"
    elif not load_chunks(settings.knowledge_base_path):
        checks["knowledge_base"] = "empty"
    else:
        checks["knowledge_base"] = "ok"

    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "unavailable"

    status = "ready" if all(value == "ok" for value in checks.values()) else "degraded"
    return HealthStatus(status=status, checks=checks)
