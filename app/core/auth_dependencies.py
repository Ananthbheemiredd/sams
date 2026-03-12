from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.base import get_session
from app.models.user_models import User
from app.models.user_session import UserSession
from app.core.permissions import PERMISSIONS
from app.utils.jwt_helper import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============================================================
# 1. VALIDATE ACCESS TOKEN + SESSION + MFA
# ============================================================
async def require_access_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(401, "Invalid or expired token")

    if payload.get("token_type") != "access":
        raise HTTPException(403, "Access token required")

    if not payload.get("mfa_verified"):
        raise HTTPException(403, "MFA verification required")

    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(401, "Invalid session")

    result = await db.execute(
        select(UserSession).where(
            UserSession.session_id == session_id,
            UserSession.is_active.is_(True),
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(401, "Session expired or logged out")

    if session.jwt_token != token:
        raise HTTPException(401, "Session invalidated")

    return payload


# ============================================================
# 2. GET CURRENT USER (after token validation)
# ============================================================
async def get_current_user(
    payload: dict = Depends(require_access_token),
    db: AsyncSession = Depends(get_session),
):
    user_id = int(payload["sub"])

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(401, "User not found")

    return user


# ============================================================
# 3. ROLE CHECK (simple)
# ============================================================
def require_roles(*roles: str):
    async def checker(user: User = Depends(get_current_user)):
        if user.role_type not in roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have required role"
            )
        return user
    return checker


# ============================================================
# 4. PERMISSION CHECK (advanced)
# ============================================================
def require_permission(permission: str):
    async def checker(user: User = Depends(get_current_user)):
        role_permissions = PERMISSIONS.get(user.role_type, {})

        if permission not in role_permissions:
            raise HTTPException(
                403, f"Permission '{permission}' not defined for role"
            )

        if not role_permissions[permission]:
            raise HTTPException(
                403, f"You do not have permission: {permission}"
            )

        return user
    return checker
