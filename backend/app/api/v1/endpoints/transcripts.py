import os
import json
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models import Appointment, Transcript, Report, User
from app.api.v1.deps import get_current_doctor
from app.core.config import settings

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


async def process_audio(appointment_id: str, file_path: str, db: AsyncSession):
    """Background task: run Whisper transcription then generate report."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # 1. Get transcript record
    result = await db.execute(select(Transcript).where(Transcript.appointment_id == appointment_id))
    transcript = result.scalar_one_or_none()
    if not transcript:
        return

    try:
        transcript.status = "processing"
        await db.commit()

        # 2. Whisper transcription
        with open(file_path, "rb") as audio_file:
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
            )

        transcript.raw_text = response.text
        transcript.language_detected = response.language
        transcript.duration_seconds = int(response.duration) if hasattr(response, "duration") else None
        transcript.status = "ready"
        await db.commit()

        # 3. Auto-generate report from transcript
        await generate_report_from_transcript(appointment_id, transcript.raw_text, transcript.id, db)

    except Exception as e:
        transcript.status = "failed"
        await db.commit()


async def generate_report_from_transcript(appointment_id: str, transcript_text: str, transcript_id: UUID, db: AsyncSession):
    """Send transcript to LLM and create a draft report."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""You are a medical assistant. Analyse this doctor-patient consultation transcript and extract structured information.

Transcript:
{transcript_text}

Return ONLY valid JSON with this exact structure:
{{
  "chief_complaint": "main reason for the visit in one sentence",
  "symptoms": ["symptom 1", "symptom 2"],
  "diagnosis": "suggested diagnosis or differential",
  "treatment_plan": "recommended treatment",
  "medications": [
    {{"name": "medication name", "dose": "dose", "frequency": "frequency", "duration": "duration"}}
  ],
  "follow_up_date": null,
  "summary": "brief consultation summary"
}}
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    raw = json.loads(response.choices[0].message.content)

    # Check if a report already exists
    result = await db.execute(select(Report).where(Report.appointment_id == appointment_id))
    report = result.scalar_one_or_none()

    if not report:
        report = Report(appointment_id=appointment_id, transcript_id=transcript_id)
        db.add(report)

    report.chief_complaint = raw.get("chief_complaint")
    report.symptoms = raw.get("symptoms", [])
    report.diagnosis = raw.get("diagnosis")
    report.treatment_plan = raw.get("treatment_plan")
    report.medications = raw.get("medications", [])
    report.ai_raw_output = raw
    report.status = "draft"
    await db.commit()


@router.post("/calls/{appointment_id}/recording", status_code=202)
async def upload_recording(
    appointment_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    # Verify appointment belongs to doctor
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id, Appointment.doctor_id == current_user.id)
    )
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Save audio file
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(settings.LOCAL_STORAGE_PATH, f"{appointment_id}.webm")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Update transcript record
    t_result = await db.execute(select(Transcript).where(Transcript.appointment_id == appointment_id))
    transcript = t_result.scalar_one_or_none()
    if not transcript:
        transcript = Transcript(appointment_id=appointment_id, status="pending")
        db.add(transcript)
        await db.flush()

    transcript.audio_file_url = file_path
    await db.commit()

    # Kick off background processing
    background_tasks.add_task(process_audio, str(appointment_id), file_path, db)

    return {"message": "Audio received. Transcription in progress.", "appointment_id": str(appointment_id)}


@router.get("/{appointment_id}")
async def get_transcript(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_doctor),
):
    result = await db.execute(select(Transcript).where(Transcript.appointment_id == appointment_id))
    transcript = result.scalar_one_or_none()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript
