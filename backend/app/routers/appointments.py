from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..metrics import APPOINTMENT_STATUS_CHANGES, APPOINTMENTS_BOOKED
from ..models import Appointment, Doctor
from ..schemas import AppointmentCreate, AppointmentOut, AppointmentUpdate, StatsOut, Status

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

# Which status an appointment may move to from its current status.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "SCHEDULED": {"CHECKED_IN", "CANCELLED"},
    "CHECKED_IN": {"COMPLETED", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}
MAX_DURATION = timedelta(minutes=180)


def as_utc(value: datetime) -> datetime:
    """SQLite drops tzinfo, so treat naive datetimes as UTC everywhere."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def to_out(appt: Appointment) -> AppointmentOut:
    return AppointmentOut(
        id=appt.id,
        patient_name=appt.patient_name,
        patient_phone=appt.patient_phone,
        doctor_id=appt.doctor_id,
        doctor_name=appt.doctor.name,
        specialty=appt.doctor.specialty,
        scheduled_at=as_utc(appt.scheduled_at),
        duration_minutes=appt.duration_minutes,
        reason=appt.reason,
        status=appt.status,
        created_at=as_utc(appt.created_at),
    )


def get_or_404(db: Session, appointment_id: int) -> Appointment:
    appt = db.get(Appointment, appointment_id, options=[joinedload(Appointment.doctor)])
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


def ensure_doctor(db: Session, doctor_id: int) -> Doctor:
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


def ensure_slot_free(db: Session, doctor_id: int, start: datetime, minutes: int, ignore_id: int | None = None):
    """Reject the booking if it overlaps another active appointment for the same doctor."""
    start = as_utc(start)
    end = start + timedelta(minutes=minutes)
    candidates = db.scalars(
        select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.status != "CANCELLED",
            Appointment.scheduled_at > start - MAX_DURATION,
            Appointment.scheduled_at < end,
        )
    )
    for other in candidates:
        if other.id == ignore_id:
            continue
        other_start = as_utc(other.scheduled_at)
        other_end = other_start + timedelta(minutes=other.duration_minutes)
        if other_start < end and start < other_end:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Doctor already has an appointment at {other_start:%Y-%m-%d %H:%M} UTC",
            )


@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    status_filter: Status | None = Query(default=None, alias="status"),
    doctor_id: int | None = None,
    on: date | None = Query(default=None, description="Only appointments on this UTC date"),
    db: Session = Depends(get_db),
):
    query = select(Appointment).options(joinedload(Appointment.doctor)).order_by(Appointment.scheduled_at)
    if status_filter:
        query = query.where(Appointment.status == status_filter)
    if doctor_id:
        query = query.where(Appointment.doctor_id == doctor_id)
    if on:
        day_start = datetime.combine(on, time.min, tzinfo=UTC)
        query = query.where(
            Appointment.scheduled_at >= day_start, Appointment.scheduled_at < day_start + timedelta(days=1)
        )
    return [to_out(a) for a in db.scalars(query)]


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    rows = db.execute(select(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status)).all()
    counts = {row_status: count for row_status, count in rows}
    day_start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    today = db.scalar(
        select(func.count(Appointment.id)).where(
            Appointment.scheduled_at >= day_start, Appointment.scheduled_at < day_start + timedelta(days=1)
        )
    )
    return StatsOut(
        total=sum(counts.values()),
        today=today or 0,
        scheduled=counts.get("SCHEDULED", 0),
        checkedIn=counts.get("CHECKED_IN", 0),
        completed=counts.get("COMPLETED", 0),
        cancelled=counts.get("CANCELLED", 0),
        doctors=db.scalar(select(func.count(Doctor.id))) or 0,
    )


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return to_out(get_or_404(db, appointment_id))


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    doctor = ensure_doctor(db, payload.doctor_id)
    ensure_slot_free(db, payload.doctor_id, payload.scheduled_at, payload.duration_minutes)
    data = payload.model_dump()
    data["scheduled_at"] = as_utc(payload.scheduled_at)
    appt = Appointment(**data, status="SCHEDULED")
    db.add(appt)
    db.commit()
    APPOINTMENTS_BOOKED.labels(specialty=doctor.specialty).inc()
    return to_out(get_or_404(db, appt.id))


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db)):
    appt = get_or_404(db, appointment_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)

    old_status = appt.status
    new_status = changes.get("status")
    if new_status and new_status != old_status and new_status not in ALLOWED_TRANSITIONS[old_status]:
        raise HTTPException(status_code=409, detail=f"Cannot move appointment from {appt.status} to {new_status}")

    if {"doctor_id", "scheduled_at", "duration_minutes"} & changes.keys():
        doctor_id = changes.get("doctor_id", appt.doctor_id)
        ensure_doctor(db, doctor_id)
        ensure_slot_free(
            db,
            doctor_id,
            changes.get("scheduled_at", appt.scheduled_at),
            changes.get("duration_minutes", appt.duration_minutes),
            ignore_id=appt.id,
        )
    if "scheduled_at" in changes:
        changes["scheduled_at"] = as_utc(changes["scheduled_at"])

    for key, value in changes.items():
        setattr(appt, key, value)
    db.commit()
    if new_status and new_status != old_status:
        APPOINTMENT_STATUS_CHANGES.labels(status=new_status).inc()
    db.expire_all()
    return to_out(get_or_404(db, appointment_id))


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = get_or_404(db, appointment_id)
    db.delete(appt)
    db.commit()
