# app/core/security.py
from fastapi import HTTPException, Depends, status
from app.core.permissions import PERMISSIONS
from app.core.role_deps import get_current_user
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def require_permission(permission: str):
    def wrapper(user = Depends(get_current_user)):
        allowed = PERMISSIONS.get(getattr(user, "role_type", None), [])
        # fallback to role relation name if role_type missing
        if not allowed:
            role_rel = getattr(user, "role", None)
            if role_rel and hasattr(role_rel, "name"):
                allowed = PERMISSIONS.get(role_rel.name, [])

        if "ALL" in allowed or permission in allowed:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return wrapper
