# app/utils/jwt_helper.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt

from app.core.config import settings

ALGORITHM = settings.JWT_ALGORITHM
SECRET = settings.SECRET_KEY


# ============================================================
# CREATE TOKEN (ACCESS or TEMP)
# ============================================================
def create_access_token(
    data: Dict[str, Any],
    expires_minutes: Optional[int] = None,
) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=(expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)


# ============================================================
# CREATE TEMP MFA TOKEN (USED IN LOGIN STEP 1)
# ============================================================
def create_temp_token(user_id: int, role: str) -> str:
    data = {
        "sub": str(user_id),
        "role": role,
        "token_type": "temp",      # ✅ REQUIRED
        "mfa_verified": False,
    }
    return create_access_token(data, expires_minutes=10)


# ============================================================
# DECODE TOKEN
# ============================================================
def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            SECRET,
            algorithms=[ALGORITHM],
        )
        return payload
    except Exception:
        return None


# ============================================================
# VALIDATE TEMP TOKEN (USED IN MFA ROUTER)
# ============================================================
def require_temp_ticket(token: str) -> Dict[str, str]:
    claims = decode_access_token(token)

    if not claims:
        raise Exception("Invalid or expired temp token")

    if claims.get("token_type") != "temp":
        raise Exception("This is not a temp MFA token")

    return {
        "user_id": str(claims["sub"]),
        "role": str(claims["role"]),
    }


# ============================================================
# EXTRACT TOKEN FROM HEADER OR PARAM
# ============================================================
def extract_token(token: Optional[str], authorization: Optional[str] = None) -> str:
    if token:
        return token

    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1]

    raise Exception("Token missing")
