from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.db_models import CallLog
from app.schemas import CallLogResponse

router = APIRouter(tags=["logs"])


@router.get("/logs", response_model=list[CallLogResponse])
def list_logs(db: Session = Depends(get_db)) -> list[CallLog]:
    rows = db.execute(select(CallLog).order_by(CallLog.id.desc())).scalars().all()
    return list(rows)
