from fastapi import APIRouter
from app.api.v1.endpoints import auth, doctors, patients, appointments, transcripts, reports

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(doctors.router)
api_router.include_router(patients.router)
api_router.include_router(appointments.router)
api_router.include_router(transcripts.router)
api_router.include_router(reports.router)
