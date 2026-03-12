# app/routers/mfa_router.py

import io
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import pyotp
import qrcode
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import StreamingResponse

from app.database.base import get_session
from app.models.mfa_secret import MFASecret
from app.models.user_session import UserSession
from app.schemas.mfa_schema import LoginVerifyIn
from app.utils.jwt_helper import (
    create_access_token,
    decode_access_token,
    extract_token,
    require_temp_ticket,
)
from app.utils.session_utils import create_user_session

router = APIRouter(prefix="/mfa", tags=["MFA"])

IST = timezone(timedelta(hours=5, minutes=30))


def now_ist():
    return datetime.now(IST).replace(tzinfo=None)


# ============================================================
# COMMON HELPER
# ============================================================
async def get_mfa_or_404(db: AsyncSession, user_id: int, role: str):
    q = await db.execute(
        select(MFASecret).where(
            MFASecret.user_id == user_id,
            MFASecret.role_type == role,
        )
    )
    mfa = q.scalar_one_or_none()
    if not mfa:
        raise HTTPException(404, "MFA record not found")
    return mfa


# ============================================================
# ENROLL START → RETURNS OTPAUTH URL
# ============================================================
@router.post("/enroll/start")
async def enroll_start(
    token: str = Query(...),
    db: AsyncSession = Depends(get_session),
):
    claims = require_temp_ticket(token)
    user_id = int(claims["user_id"])
    role = claims["role"]

    mfa = await get_mfa_or_404(db, user_id, role)

    # Generate secret if not present
    if not mfa.secret_key:
        mfa.secret_key = pyotp.random_base32()
        await db.commit()
        await db.refresh(mfa)

    uri = pyotp.TOTP(mfa.secret_key).provisioning_uri(
        name=f"SAMS:{user_id}",
        issuer_name="SAMS",
    )

    return {"otpauth_url": uri}


# ============================================================
# ENROLL QR IMAGE
# ============================================================
@router.get("/enroll/qr")
async def enroll_qr(token: str, db: AsyncSession = Depends(get_session)):
    payload = decode_access_token(token)

    if not payload or payload.get("token_type") != "temp":
        raise HTTPException(400, "Temporary token required")

    user_id = int(payload["sub"])
    role = payload["role"]

    mfa = await get_mfa_or_404(db, user_id, role)

    if not mfa.secret_key:
        mfa.secret_key = pyotp.random_base32()
        await db.commit()
        await db.refresh(mfa)

    otp_uri = pyotp.TOTP(mfa.secret_key).provisioning_uri(
        name=f"SAMS:{user_id}",
        issuer_name="SAMS",
    )

    qr = qrcode.make(otp_uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


# ============================================================
# ENROLL VERIFY
# ============================================================
@router.post("/enroll/verify")
async def enroll_verify(
    code: str = Query(...),
    token: str = Query(...),
    db: AsyncSession = Depends(get_session),
):
    claims = require_temp_ticket(token)
    user_id = int(claims["user_id"])
    role = claims["role"]

    mfa = await get_mfa_or_404(db, user_id, role)

    if mfa.is_verified:
        raise HTTPException(409, "MFA already verified")

    if not pyotp.TOTP(mfa.secret_key).verify(code, valid_window=1):
        raise HTTPException(400, "Invalid OTP")

    raw_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    mfa.backup_codes = [hashlib.sha256(c.encode()).hexdigest() for c in raw_codes]
    mfa.is_verified = True
    mfa.enrolled_at = now_ist()
    mfa.last_verified_at = now_ist()

    await db.commit()

    return {"backup_codes": raw_codes}


# ============================================================
# VERIFY LOGIN (STEP 2 AFTER /auth/login)
# ============================================================
@router.post("/verify-login")
async def verify_login(
    data: LoginVerifyIn,
    db: AsyncSession = Depends(get_session),
):
    token = extract_token(data.temp_token)
    claims = require_temp_ticket(token)

    user_id = int(claims["user_id"])
    role = claims["role"]

    mfa = await get_mfa_or_404(db, user_id, role)

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

    # Create DB session
    session = await create_user_session(db, user_id, role)

    access_token = create_access_token(
        {
            "sub": str(user_id),
            "role": role,
            "mfa_verified": True,
            "token_type": "access",
            "session_id": session["session_id"],
        }
    )

    await db.execute(
        update(UserSession)
        .where(UserSession.session_id == session["session_id"])
        .values(jwt_token=access_token)
    )
    await db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "session_id": session["session_id"],
    }


# ============================================================
# BACKUP CODE ROTATE
# ============================================================
@router.post("/backup/rotate")
async def rotate_backup(
    token: str = Query(...),
    code: str = Query(...),
    db: AsyncSession = Depends(get_session),
):
    payload = decode_access_token(token)

    if not payload or not payload.get("mfa_verified"):
        raise HTTPException(401, "Invalid token")

    user_id = int(payload["sub"])
    role = payload["role"]

    mfa = await get_mfa_or_404(db, user_id, role)

    if not pyotp.TOTP(mfa.secret_key).verify(code, valid_window=1):
        raise HTTPException(400, "Invalid OTP")

    raw = [secrets.token_hex(4).upper() for _ in range(10)]
    mfa.backup_codes = [hashlib.sha256(c.encode()).hexdigest() for c in raw]
    await db.commit()

    return {"backup_codes": raw}


# ============================================================
# DISABLE MFA
# ============================================================
@router.post("/disable")
async def disable_mfa(
    token: str = Query(...),
    code: str = Query(...),
    db: AsyncSession = Depends(get_session),
):
    payload = decode_access_token(token)

    user_id = int(payload["sub"])
    role = payload["role"]

    mfa = await get_mfa_or_404(db, user_id, role)

    totp_ok = pyotp.TOTP(mfa.secret_key).verify(code, valid_window=1)
    hashed = hashlib.sha256(code.encode()).hexdigest()

    if not (totp_ok or (mfa.backup_codes and hashed in mfa.backup_codes)):
        raise HTTPException(400, "Invalid MFA code")

    mfa.secret_key = None
    mfa.is_verified = False
    mfa.backup_codes = []
    mfa.enrolled_at = None
    mfa.last_verified_at = None

    await db.commit()

    return {"message": "MFA disabled successfully"}

# ============================================================
# RE-ENROLL START (user already has MFA, wants new device)
# ============================================================
@router.post("/re-enroll/start")
async def re_enroll_start(
    token: str = Query(...),
    db: AsyncSession = Depends(get_session),
):
    claims = require_temp_ticket(token)
    user_id = int(claims["user_id"])
    role = claims["role"]

    mfa = await get_mfa_or_404(db, user_id, role)

    if not mfa.is_verified:
        raise HTTPException(400, "MFA is not yet enrolled")

    # 🔥 invalidate old MFA completely
    mfa.secret_key = pyotp.random_base32()
    mfa.is_verified = False
    mfa.backup_codes = []
    mfa.enrolled_at = None
    mfa.last_verified_at = None

    await db.commit()
    await db.refresh(mfa)

    uri = pyotp.TOTP(mfa.secret_key).provisioning_uri(
        name=f"SAMS:{user_id}",
        issuer_name="SAMS",
    )

    return {
        "message": "Re-enrollment started. Scan new QR.",
        "otpauth_url": uri,
    }

# ============================================================
# RE-ENROLL VERIFY
# ============================================================
@router.post("/re-enroll/verify")
async def re_enroll_verify(
    token: str = Query(...),
    code: str = Query(...),
    db: AsyncSession = Depends(get_session),
):
    claims = require_temp_ticket(token)
    user_id = int(claims["user_id"])
    role = claims["role"]

    mfa = await get_mfa_or_404(db, user_id, role)

    if mfa.is_verified:
        raise HTTPException(409, "MFA already verified")

    if not pyotp.TOTP(mfa.secret_key).verify(code, valid_window=1):
        raise HTTPException(400, "Invalid OTP")

    raw_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    mfa.backup_codes = [hashlib.sha256(c.encode()).hexdigest() for c in raw_codes]
    mfa.is_verified = True
    mfa.enrolled_at = now_ist()
    mfa.last_verified_at = now_ist()

    await db.commit()

    return {
        "message": "MFA re-enrolled successfully",
        "backup_codes": raw_codes,  # shown only once
    }
