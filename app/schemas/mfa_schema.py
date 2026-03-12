from pydantic import BaseModel, constr
from typing import List, Dict, Any


# =========================================================
# ENROLL START → QR generation response
# =========================================================
class MFAEnrollStartOut(BaseModel):
    user_id: str
    role: str
    otpauth_url: str


# =========================================================
# ENROLL VERIFY → user enters OTP after scanning QR
# =========================================================
class MFAEnrollVerifyIn(BaseModel):
    token: str
    code: constr(strip_whitespace=True, min_length=4, max_length=16)


class MFAEnrollVerifyOut(BaseModel):
    backup_codes: List[str]


# =========================================================
# LOGIN VERIFY (Step-2 after temp token)
# =========================================================
class LoginVerifyIn(BaseModel):
    temp_token: str
    code: constr(strip_whitespace=True, min_length=4, max_length=16)


class LoginVerifyOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =========================================================
# OPTIONAL (future safe)
# =========================================================
class BackupRotateOut(BaseModel):
    backup_codes: List[str]


class DisableMFAOut(BaseModel):
    message: str
