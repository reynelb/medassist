from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from uuid import UUID
from typing import Any
from app.models import AppointmentStatus


# ── User ──────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    photo_url: str | None = None


class UserOut(UserBase):
    id: UUID
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    photo_url: str | None = None


# ── Doctor Profile ─────────────────────────────────────────────────────────────

class DoctorProfileUpdate(BaseModel):
    specialisation: str | None = None
    clinic_name: str | None = None
    clinic_address: str | None = None
    bio: str | None = None
    languages: list[str] | None = None
    years_of_experience: int | None = None
    license_number: str | None = None


class DoctorProfileOut(DoctorProfileUpdate):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorPublicOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    photo_url: str | None
    specialisation: str | None
    clinic_name: str | None
    clinic_address: str | None
    bio: str | None
    languages: list[str] | None
    years_of_experience: int | None

    class Config:
        from_attributes = True


# ── Patient Profile ────────────────────────────────────────────────────────────

class PatientProfileUpdate(BaseModel):
    date_of_birth: date | None = None
    gender: str | None = None
    blood_type: str | None = None
    known_conditions: list[str] | None = None
    allergies: list[str] | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


class PatientNotesUpdate(BaseModel):
    doctor_notes: str


class PatientConditionsUpdate(BaseModel):
    known_conditions: list[str] | None = None
    allergies: list[str] | None = None


class PatientProfileOut(PatientProfileUpdate):
    id: UUID
    user_id: UUID
    assigned_doctor_id: UUID | None
    doctor_notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientSummaryOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    photo_url: str | None
    date_of_birth: date | None
    blood_type: str | None
    known_conditions: list[str] | None
    allergies: list[str] | None
    doctor_notes: str | None

    class Config:
        from_attributes = True


# ── Appointment ────────────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    patient_id: UUID
    scheduled_at: datetime
    reason: str | None = None


class AppointmentUpdate(BaseModel):
    scheduled_at: datetime | None = None
    reason: str | None = None
    status: AppointmentStatus | None = None


class AppointmentOut(BaseModel):
    id: UUID
    doctor_id: UUID
    patient_id: UUID
    scheduled_at: datetime
    started_at: datetime | None
    ended_at: datetime | None
    reason: str | None
    status: AppointmentStatus
    call_room_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Transcript ─────────────────────────────────────────────────────────────────

class TranscriptOut(BaseModel):
    id: UUID
    appointment_id: UUID
    raw_text: str | None
    audio_file_url: str | None
    duration_seconds: int | None
    language_detected: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Report ─────────────────────────────────────────────────────────────────────

class MedicationItem(BaseModel):
    name: str
    dose: str | None = None
    frequency: str | None = None
    duration: str | None = None


class ReportUpdate(BaseModel):
    chief_complaint: str | None = None
    symptoms: list[str] | None = None
    diagnosis: str | None = None
    treatment_plan: str | None = None
    medications: list[MedicationItem] | None = None
    follow_up_date: date | None = None
    doctor_notes: str | None = None


class ReportOut(ReportUpdate):
    id: UUID
    appointment_id: UUID
    transcript_id: UUID | None
    status: str
    is_confirmed: bool
    confirmed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Invitation ─────────────────────────────────────────────────────────────────

class InvitationOut(BaseModel):
    id: UUID
    email: str
    is_used: bool
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
