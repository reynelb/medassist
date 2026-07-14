from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models import Report, Appointment, User
from app.schemas.schemas import ReportUpdate, ReportOut
from app.api.v1.deps import get_current_doctor

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{appointment_id}", response_model=ReportOut)
async def get_report(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_doctor),
):
    result = await db.execute(select(Report).where(Report.appointment_id == appointment_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or still generating")
    return report


@router.patch("/{appointment_id}", response_model=ReportOut)
async def update_report(
    appointment_id: UUID,
    payload: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    # Verify ownership via appointment
    appt_result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id, Appointment.doctor_id == current_user.id)
    )
    if not appt_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(Report).where(Report.appointment_id == appointment_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        if field == "medications" and value is not None:
            setattr(report, field, [m.model_dump() for m in value])
        else:
            setattr(report, field, value)

    report.updated_at = datetime.utcnow()
    return report


@router.post("/{appointment_id}/confirm", response_model=ReportOut)
async def confirm_report(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    appt_result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id, Appointment.doctor_id == current_user.id)
    )
    if not appt_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(Report).where(Report.appointment_id == appointment_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.is_confirmed = True
    report.confirmed_at = datetime.utcnow()
    report.status = "confirmed"
    return report


@router.get("/patient/{patient_id}")
async def get_patient_reports(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    result = await db.execute(
        select(Report)
        .join(Appointment, Appointment.id == Report.appointment_id)
        .where(
            Appointment.patient_id == patient_id,
            Appointment.doctor_id == current_user.id,
            Report.is_confirmed == True,
        )
        .order_by(Report.created_at.desc())
    )
    return result.scalars().all()
