import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models import User, UserRole, Invitation, PatientProfile, DoctorProfile
from app.schemas.auth import (
    RegisterRequest, InviteRegisterRequest, LoginRequest,
    TokenResponse, RefreshRequest, InviteRequest
)
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.api.v1.deps import get_current_doctor
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.patient,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
    )
    db.add(user)
    await db.flush()

    profile = PatientProfile(user_id=user.id)
    db.add(profile)

    return {"message": "Account created successfully"}


@router.post("/register/invite/{token}", status_code=201)
async def register_via_invite(token: str, payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Invitation).where(Invitation.token == token, Invitation.is_used == False)
    )
    invite = result.scalar_one_or_none()
    if not invite or invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")

    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=invite.email,
        password_hash=hash_password(payload.password),
        role=UserRole.patient,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
    )
    db.add(user)
    await db.flush()

    profile = PatientProfile(user_id=user.id, assigned_doctor_id=invite.doctor_id)
    db.add(profile)

    invite.is_used = True
    return {"message": "Account created successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email, User.is_active == True))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return TokenResponse(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id)),
        role=user.role,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        result = await db.execute(select(User).where(User.id == data["sub"], User.is_active == True))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return TokenResponse(
            access_token=create_access_token(str(user.id), user.role.value),
            refresh_token=create_refresh_token(str(user.id)),
            role=user.role,
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/invite", status_code=201)
async def invite_patient(
    payload: InviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    token = secrets.token_urlsafe(32)
    invite = Invitation(
        doctor_id=current_user.id,
        email=payload.email,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(invite)
    # In production: send email with invite link
    return {"message": "Invitation sent", "token": token}


@router.get("/invite/validate/{token}")
async def validate_invite(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Invitation).where(Invitation.token == token, Invitation.is_used == False)
    )
    invite = result.scalar_one_or_none()
    if not invite or invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    return {"email": invite.email, "valid": True}
