from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models import User, UserRole, Appointment, AppointmentStatus, Transcript, Report
from app.schemas.schemas import AppointmentCreate, AppointmentUpdate, AppointmentOut
from app.api.v1.deps import get_current_user, get_current_doctor

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentOut, status_code=201)
async def create_appointment(
    payload: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    appointment = Appointment(
        doctor_id=current_user.id,
        patient_id=payload.patient_id,
        scheduled_at=payload.scheduled_at,
        reason=payload.reason,
    )
    db.add(appointment)
    await db.flush()
    return appointment


@router.get("/")
async def list_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.doctor:
        result = await db.execute(
            select(Appointment)
            .options(selectinload(Appointment.patient))
            .where(Appointment.doctor_id == current_user.id)
            .order_by(Appointment.scheduled_at.desc())
        )
    else:
        result = await db.execute(
            select(Appointment)
            .options(selectinload(Appointment.doctor))
            .where(Appointment.patient_id == current_user.id)
            .order_by(Appointment.scheduled_at.desc())
        )
    return result.scalars().all()


@router.get("/{appointment_id}")
async def get_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Appointment)
        .options(selectinload(Appointment.patient), selectinload(Appointment.doctor))
        .where(Appointment.id == appointment_id)
    )
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Patients can only see their own
    if current_user.role == UserRole.patient and appt.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return appt


@router.patch("/{appointment_id}", response_model=AppointmentOut)
async def update_appointment(
    appointment_id: UUID,
    payload: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id, Appointment.doctor_id == current_user.id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(appt, field, value)
    return appt


@router.delete("/{appointment_id}", status_code=204)
async def cancel_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id, Appointment.doctor_id == current_user.id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = AppointmentStatus.cancelled


@router.post("/{appointment_id}/start")
async def start_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id, Appointment.doctor_id == current_user.id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = AppointmentStatus.in_progress
    appt.started_at = datetime.utcnow()
    # In production: create Daily.co room here
    appt.call_room_id = f"medassist-{appointment_id}"

    return {"room_id": appt.call_room_id, "appointment_id": appointment_id}


@router.post("/{appointment_id}/end")
async def end_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id, Appointment.doctor_id == current_user.id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = AppointmentStatus.completed
    appt.ended_at = datetime.utcnow()

    # Create a pending transcript entry
    transcript = Transcript(appointment_id=appt.id, status="pending")
    db.add(transcript)

    return {"message": "Appointment ended. Upload audio to begin transcription."}
