from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models import User, UserRole, PatientProfile, Appointment
from app.schemas.schemas import PatientProfileOut, PatientNotesUpdate, PatientConditionsUpdate, DoctorPublicOut
from app.api.v1.deps import get_current_user, get_current_doctor, get_current_patient

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/me/profile")
async def get_my_profile(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_patient)):
    result = await db.execute(select(PatientProfile).where(PatientProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "photo_url": current_user.photo_url,
        "date_of_birth": profile.date_of_birth if profile else None,
        "gender": profile.gender if profile else None,
        "blood_type": profile.blood_type if profile else None,
        "known_conditions": profile.known_conditions if profile else [],
        "allergies": profile.allergies if profile else [],
    }


@router.get("/me/doctor")
async def get_my_doctor(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_patient)):
    result = await db.execute(select(PatientProfile).where(PatientProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile or not profile.assigned_doctor_id:
        raise HTTPException(status_code=404, detail="No doctor assigned")

    doctor_result = await db.execute(
        select(User).options(selectinload(User.doctor_profile))
        .where(User.id == profile.assigned_doctor_id)
    )
    doctor = doctor_result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    dp = doctor.doctor_profile
    return {
        "id": doctor.id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "photo_url": doctor.photo_url,
        "specialisation": dp.specialisation if dp else None,
        "clinic_name": dp.clinic_name if dp else None,
        "clinic_address": dp.clinic_address if dp else None,
        "bio": dp.bio if dp else None,
        "languages": dp.languages if dp else [],
        "years_of_experience": dp.years_of_experience if dp else None,
    }


@router.get("/{patient_id}/profile")
async def get_patient_profile(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    result = await db.execute(
        select(User).options(selectinload(User.patient_profile))
        .where(User.id == patient_id, User.role == UserRole.patient)
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    profile = patient.patient_profile

    # Get last 5 appointments
    appt_result = await db.execute(
        select(Appointment)
        .where(Appointment.patient_id == patient_id, Appointment.doctor_id == current_user.id)
        .order_by(Appointment.scheduled_at.desc())
        .limit(5)
    )
    appointments = appt_result.scalars().all()

    return {
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "photo_url": patient.photo_url,
        "email": patient.email,
        "date_of_birth": profile.date_of_birth if profile else None,
        "gender": profile.gender if profile else None,
        "blood_type": profile.blood_type if profile else None,
        "known_conditions": profile.known_conditions if profile else [],
        "allergies": profile.allergies if profile else [],
        "emergency_contact_name": profile.emergency_contact_name if profile else None,
        "emergency_contact_phone": profile.emergency_contact_phone if profile else None,
        "doctor_notes": profile.doctor_notes if profile else None,
        "recent_appointments": [
            {"id": a.id, "scheduled_at": a.scheduled_at, "reason": a.reason, "status": a.status}
            for a in appointments
        ],
    }


@router.patch("/{patient_id}/notes")
async def update_patient_notes(
    patient_id: UUID,
    payload: PatientNotesUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_doctor),
):
    result = await db.execute(select(PatientProfile).where(PatientProfile.user_id == patient_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    profile.doctor_notes = payload.doctor_notes
    return {"message": "Notes updated"}


@router.patch("/{patient_id}/conditions")
async def update_patient_conditions(
    patient_id: UUID,
    payload: PatientConditionsUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_doctor),
):
    result = await db.execute(select(PatientProfile).where(PatientProfile.user_id == patient_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    if payload.known_conditions is not None:
        profile.known_conditions = payload.known_conditions
    if payload.allergies is not None:
        profile.allergies = payload.allergies
    return {"message": "Conditions updated"}
