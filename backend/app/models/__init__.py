import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, Date,
    ForeignKey, Enum as SAEnum, JSON, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    doctor = "doctor"
    patient = "patient"


class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    photo_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    doctor_profile: Mapped["DoctorProfile | None"] = relationship("DoctorProfile", back_populates="user", uselist=False)
    patient_profile: Mapped["PatientProfile | None"] = relationship("PatientProfile", back_populates="user", uselist=False, foreign_keys="PatientProfile.user_id")


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    specialisation: Mapped[str | None] = mapped_column(String(100))
    clinic_name: Mapped[str | None] = mapped_column(String(150))
    clinic_address: Mapped[str | None] = mapped_column(Text)
    bio: Mapped[str | None] = mapped_column(Text)
    languages: Mapped[list | None] = mapped_column(ARRAY(String))
    years_of_experience: Mapped[int | None] = mapped_column(Integer)
    license_number: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="doctor_profile")


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    assigned_doctor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    date_of_birth: Mapped[datetime | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    blood_type: Mapped[str | None] = mapped_column(String(5))
    known_conditions: Mapped[list | None] = mapped_column(ARRAY(String))
    allergies: Mapped[list | None] = mapped_column(ARRAY(String))
    emergency_contact_name: Mapped[str | None] = mapped_column(String(150))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20))
    doctor_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="patient_profile", foreign_keys=[user_id])
    assigned_doctor: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_doctor_id])


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[AppointmentStatus] = mapped_column(SAEnum(AppointmentStatus), default=AppointmentStatus.scheduled)
    call_room_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    doctor: Mapped["User"] = relationship("User", foreign_keys=[doctor_id])
    patient: Mapped["User"] = relationship("User", foreign_keys=[patient_id])
    transcript: Mapped["Transcript | None"] = relationship("Transcript", back_populates="appointment", uselist=False)
    report: Mapped["Report | None"] = relationship("Report", back_populates="appointment", uselist=False)


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("appointments.id"), unique=True)
    raw_text: Mapped[str | None] = mapped_column(Text)
    audio_file_url: Mapped[str | None] = mapped_column(Text)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    language_detected: Mapped[str | None] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | processing | ready | failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="transcript")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("appointments.id"), unique=True)
    transcript_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("transcripts.id"))
    chief_complaint: Mapped[str | None] = mapped_column(Text)
    symptoms: Mapped[list | None] = mapped_column(ARRAY(String))
    diagnosis: Mapped[str | None] = mapped_column(Text)
    treatment_plan: Mapped[str | None] = mapped_column(Text)
    medications: Mapped[dict | None] = mapped_column(JSON)
    follow_up_date: Mapped[datetime | None] = mapped_column(Date)
    doctor_notes: Mapped[str | None] = mapped_column(Text)
    ai_raw_output: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | draft | confirmed
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="report")


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    doctor: Mapped["User"] = relationship("User", foreign_keys=[doctor_id])
