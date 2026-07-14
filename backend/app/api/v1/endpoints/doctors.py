from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models import User, UserRole, DoctorProfile, PatientProfile, Appointment, AppointmentStatus
from app.schemas.schemas import DoctorProfileUpdate, DoctorProfileOut, DoctorPublicOut, PatientSummaryOut
from app.api.v1.deps import get_current_user, get_current_doctor
from datetime import datetime, date

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/{doctor_id}/profile", response_model=DoctorPublicOut)
async def get_doctor_profile(doctor_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(User).options(selectinload(User.doctor_profile))
        .where(User.id == doctor_id, User.role == UserRole.doctor)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    profile = doctor.doctor_profile
    return DoctorPublicOut(
        id=doctor.id,
        first_name=doctor.first_name,
        last_name=doctor.last_name,
        photo_url=doctor.photo_url,
        specialisation=profile.specialisation if profile else None,
        clinic_name=profile.clinic_name if profile else None,
        clinic_address=profile.clinic_address if profile else None,
        bio=profile.bio if profile else None,
        languages=profile.languages if profile else None,
        years_of_experience=profile.years_of_experience if profile else None,
    )


@router.patch("/me/profile", response_model=DoctorProfileOut)
async def update_doctor_profile(
    payload: DoctorProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    result = await db.execute(select(DoctorProfile).where(DoctorProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = DoctorProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(profile, field, value)

    return profile


@router.get("/me/patients")
async def list_my_patients(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_doctor)):
    result = await db.execute(
        select(User).options(selectinload(User.patient_profile))
        .join(PatientProfile, PatientProfile.user_id == User.id)
        .where(PatientProfile.assigned_doctor_id == current_user.id)
    )
    patients = result.scalars().all()
    return [
        {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "photo_url": p.photo_url,
            "date_of_birth": p.patient_profile.date_of_birth if p.patient_profile else None,
            "known_conditions": p.patient_profile.known_conditions if p.patient_profile else [],
        }
        for p in patients
    ]


@router.get("/me/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_doctor)):
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    result = await db.execute(
        select(Appointment)
        .options(selectinload(Appointment.patient))
        .where(
            Appointment.doctor_id == current_user.id,
            Appointment.scheduled_at >= today_start,
            Appointment.scheduled_at <= today_end,
        )
        .order_by(Appointment.scheduled_at)
    )
    today_appointments = result.scalars().all()

    patient_count_result = await db.execute(
        select(PatientProfile).where(PatientProfile.assigned_doctor_id == current_user.id)
    )
    patient_count = len(patient_count_result.scalars().all())

    return {
        "today_appointments": [
            {
                "id": a.id,
                "patient_name": f"{a.patient.first_name} {a.patient.last_name}",
                "patient_photo": a.patient.photo_url,
                "scheduled_at": a.scheduled_at,
                "reason": a.reason,
                "status": a.status,
            }
            for a in today_appointments
        ],
        "stats": {
            "total_patients": patient_count,
            "today_appointments": len(today_appointments),
        },
    }
