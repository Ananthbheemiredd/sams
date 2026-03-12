from fastapi import APIRouter, Depends, HTTPException
from app.core.role_deps import (
    get_current_user,
    require_admission_manager,
    require_roles,
    extract_role_name
)
from app.models.user_models import User
from app.core.permissions import PERMISSIONS

router = APIRouter(prefix="/rbac", tags=["Dynamic RBAC"])


# -----------------------------------------------------------
# WHO AM I
# -----------------------------------------------------------
@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role_type,
    }


# -----------------------------------------------------------
# DYNAMIC PERMISSION CHECK ENDPOINT
# -----------------------------------------------------------
@router.get("/allow/{permission}")
async def dynamic_permission_check(
    permission: str,
    user: User = Depends(get_current_user),  # IMPORTANT FIX!
    allowed: bool = Depends(require_admission_manager)  # Will validate automatically
):
    return {
        "permission": permission,
        "allowed": allowed,
        "user": user.email,
        "role": user.role_type,
    }

# =====================================================
# DYNAMIC ROLE RESTRICTED ENDPOINT
# =====================================================
@router.get("/only/{role_name}")
async def dynamic_role_check(
    role_name: str,
    user: User = Depends(get_current_user)
):
    """
    Allows only one specific role.
    Example:
    /rbac/only/ADMIN
    /rbac/only/HR
    /rbac/only/TEACHER
    """
    user_role = extract_role_name(user._token_payload)

    if user_role == "SUPER_ADMIN":
        return {"allowed": True, "role": user_role}

    if user_role != role_name:
        raise HTTPException(403, f"Only {role_name} can access this endpoint")

    return {"allowed": True, "role": user_role}
