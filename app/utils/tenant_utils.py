from fastapi import HTTPException

ALLOWED_ADMIN_ROLES = {"ADMIN", "SUPER_ADMIN"}

def ensure_super_admin(role: str):
    """
    Allows ADMIN and SUPER_ADMIN only
    """
    if role not in ALLOWED_ADMIN_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Admin or Super Admin access required"
        )
