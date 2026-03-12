# app/core/role_deps.py
from fastapi import Depends, HTTPException, Header, status
from typing import Callable, Optional, Any
from app.utils.jwt_helper import decode_access_token
from app.models.user_models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.base import get_session
from app.core.permissions import PERMISSIONS


# ---------------------------------------------------------
# Get current user
# ---------------------------------------------------------
async def get_current_user(
    Authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_session)
) -> User:

    if not Authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization format")

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    # ensure sub exists and is integer-convertible
    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # keep token payload on user for later checks
    user._token_payload = payload

    return user


# ---------------------------------------------------------
# Extract role (helper)
# ---------------------------------------------------------
def extract_role_name(payload: dict) -> Optional[str]:
    return payload.get("role")


# ---------------------------------------------------------
# ROLE VALIDATOR (STATIC ROLE CHECK)
# Returns a callable to be used with Depends(...)
# Example usage: Depends(require_roles("ADMIN", "SUPER_ADMIN"))
# ---------------------------------------------------------
def require_roles(*allowed_roles: str) -> Callable[..., Any]:
    async def wrapper(user: User = Depends(get_current_user)):
        role = None
        # prefer explicit token role if present
        if hasattr(user, "_token_payload") and user._token_payload:
            role = user._token_payload.get("role")
        # fallback to model property
        if not role:
            role = getattr(user, "role_type", None) or getattr(user, "role", None)
            # if role is an object (e.g. Role model), try to extract name
            if hasattr(role, "name"):
                role = role.name

        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Role not permitted")
        return user

    return wrapper


# ---------------------------------------------------------
# PERMISSION CORE (DYNAMIC RBAC)
# ---------------------------------------------------------
async def _permission_core(permission: str, user: User) -> bool:
    # Determine role name
    role = getattr(user, "role_type", None)
    if not role:
        # try role relation
        role_rel = getattr(user, "role", None)
        if role_rel and hasattr(role_rel, "name"):
            role = role_rel.name

    # SUPER ADMIN bypass (explicit)
    if role == "SUPER_ADMIN":
        return True

    if role not in PERMISSIONS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role has no permissions assigned")

    allowed_perms = PERMISSIONS.get(role, [])
    # PERMISSIONS[role] can be list or dict depending on your scheme; handle both
    if isinstance(allowed_perms, dict):
        has = permission in allowed_perms and bool(allowed_perms.get(permission))
    else:
        has = (permission in allowed_perms) or ("ALL" in allowed_perms)

    if not has:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{role}' does NOT have permission '{permission}'"
        )

    return True


# ---------------------------------------------------------
# Permission factory for FastAPI dependencies
# Usage: user = Depends(Permission("ADMISSIONS"))
# ---------------------------------------------------------
def Permission(permission: str) -> Callable[..., Any]:
    async def wrapper(user: User = Depends(get_current_user)):
        await _permission_core(permission, user)
        # return user so downstream endpoints can use it
        return user

    return wrapper


# ---------------------------------------------------------

# ---------------------------------------------------------
require_admission_manager = Permission("ADMISSIONS")
require_fee_manager = Permission("FEE_TRACKING")
require_exam_manager = Permission("EXAM_MANAGEMENT")
require_hostel_manager = Permission("ROOM_ALLOCATION")
require_hr_manager = Permission("PAYROLL")
