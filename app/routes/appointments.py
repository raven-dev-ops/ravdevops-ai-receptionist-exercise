from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.db_models import Appointment
from app.schemas import AppointmentResponse

router = APIRouter(tags=["appointments"])


@router.get("/appointments", response_model=list[AppointmentResponse])
def list_appointments(db: Session = Depends(get_db)) -> list[Appointment]:
    rows = db.execute(select(Appointment).order_by(Appointment.id.desc())).scalars().all()
    return list(rows)
