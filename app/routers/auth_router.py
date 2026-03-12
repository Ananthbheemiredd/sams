import hashlib
import os
from datetime import datetime

import pyotp
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_session
from app.models.user_models import User
from app.models.user_details import UserDetail
from app.models.mfa_secret import MFASecret
from app.models.user_session import UserSession

from app.schemas.mfa_schema import LoginVerifyIn
from app.schemas.user_schemas import RegisterRequest, LogoutRequest


from app.utils.password import hash_password, verify_password
from app.utils.jwt_helper import (
    create_access_token,
    extract_token,
    require_temp_ticket,
)
from app.utils.session_utils import create_user_session
from app.core.permissions import PERMISSIONS
from app.core.auth_dependencies import require_access_token
from app.routers.mfa_router import get_mfa_or_404, now_ist

router = APIRouter(prefix="/auth", tags=["Authentication"])

SUPER_ADMIN_SECRET = os.getenv("SUPER_ADMIN_SECRET")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


@router.post("/register")
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_session),
    x_secret_key: str = Header(None),
):
    if x_secret_key != SUPER_ADMIN_SECRET:
        raise HTTPException(403, "Invalid x-secret-key")

    role = payload.role_type.upper()
    if role not in PERMISSIONS:
        raise HTTPException(400, "Invalid role")

    # Check existing email
    exists = (
        await db.execute(select(User).where(User.email == payload.email))
    ).scalar_one_or_none()

    if exists:
        raise HTTPException(400, "Email already exists")

    # Create User
    user = User(
        username=payload.username,
        email=payload.email,
        password=hash_password(payload.password),
        role_type=role,
    )
    db.add(user)
    await db.flush()  # <-- gets auto-generated user_id

    # Create UserDetail
    db.add(
        UserDetail(
            user_id=user.user_id,   #  FIXED
            full_name=payload.username,
            role=role,
            school_id=payload.school_id,     # REQUIRED in your model
            branch_id=payload.branch_id,     # REQUIRED in your model
        )
    )

    # Create MFA Secret
    db.add(
        MFASecret(
            user_id=user.user_id,   #  FIXED
            role_type=role
        )
    )

    await db.commit()

    return {
        "message": "User registered. MFA enrollment required.",
        "user_id": user.user_id,   #  FIXED
        "role": role,
    }


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    user = (
        await db.execute(
            select(User).where(User.email == form_data.username)
        )
    ).scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(400, "Invalid credentials")

    mfa = (
        await db.execute(
            select(MFASecret).where(MFASecret.user_id == user.user_id)
        )
    ).scalar_one_or_none()

    temp_token = create_access_token(
        {
            "sub": str(user.user_id),
            "role": user.role_type,
            "token_type": "temp",
            "mfa_verified": False,
        },
        expires_minutes=10,
    )

    if not mfa:
        next_step = "setup_mfa"
    elif not mfa.is_verified:
        next_step = "verify_mfa"
    else:
        next_step = "login_mfa"

    return {
        "temp_token": temp_token,
        "next_step": next_step,
    }


@router.post("/verify-login")
async def verify_login(
    data: LoginVerifyIn,
    db: AsyncSession = Depends(get_session),
):
    token = extract_token(data.temp_token)

    claims = require_temp_ticket(token)
    user_id = int(claims["sub"])
    role = claims["role"]

    mfa = await get_mfa_or_404(db, user_id, role)

    if not mfa.secret_key or not mfa.is_verified:
        raise HTTPException(400, "MFA not enrolled")

    totp_ok = pyotp.TOTP(mfa.secret_key).verify(data.code, valid_window=1)

    backup_ok = False
    if not totp_ok and mfa.backup_codes:
        hashed = hashlib.sha256(data.code.encode()).hexdigest()
        if hashed in mfa.backup_codes:
            mfa.backup_codes.remove(hashed)
            backup_ok = True

    if not (totp_ok or backup_ok):
        raise HTTPException(400, "Invalid MFA code")

    mfa.last_verified_at = now_ist()
    await db.commit()

    session = await create_user_session(db, user_id, role)

    access_token = create_access_token(
        {
            "sub": str(user_id),
            "role": role,
            "token_type": "access",
            "session_id": session["session_id"],
            "mfa_verified": True,
        }
    )

    await db.execute(
        update(UserSession)
        .where(UserSession.session_id == session["session_id"])
        .values(jwt_token=access_token)
    )
    await db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_session),
):
    session = (
        await db.execute(
            select(UserSession).where(
                UserSession.session_id == payload.session_id,
                UserSession.is_active.is_(True),
            )
        )
    ).scalar_one_or_none()

    if not session:
        raise HTTPException(404, "Session not found")

    session.is_active = False
    session.logout_time = datetime.utcnow()
    await db.commit()

    return {"message": "Logged out successfully"}

@router.get("/me")
async def me(payload: dict = Depends(require_access_token)):
    return payload
