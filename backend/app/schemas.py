from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["SCHEDULED", "CHECKED_IN", "COMPLETED", "CANCELLED"]


class DoctorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    specialty: str = Field(min_length=2, max_length=80)
    room: str = Field(default="", max_length=20)


class DoctorOut(DoctorCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
    patient_name: str = Field(min_length=2, max_length=120)
    patient_phone: str = Field(default="", max_length=20)
    doctor_id: int
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=10, le=180)
    reason: str = ""


class AppointmentUpdate(BaseModel):
    patient_name: str | None = Field(default=None, min_length=2, max_length=120)
    patient_phone: str | None = Field(default=None, max_length=20)
    doctor_id: int | None = None
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=10, le=180)
    reason: str | None = None
    status: Status | None = None


class AppointmentOut(BaseModel):
    id: int
    patient_name: str
    patient_phone: str
    doctor_id: int
    doctor_name: str
    specialty: str
    scheduled_at: datetime
    duration_minutes: int
    reason: str
    status: Status
    created_at: datetime


class StatsOut(BaseModel):
    total: int
    today: int
    scheduled: int
    checkedIn: int
    completed: int
    cancelled: int
    doctors: int
