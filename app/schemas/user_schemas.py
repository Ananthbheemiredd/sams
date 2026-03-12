from pydantic import BaseModel, EmailStr, constr
from typing import Optional


# ======================================================
# REGISTER
# ======================================================

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role_type: str
    school_id: str
    branch_id: str


class RegisterResponse(BaseModel):
    message: str
    user_id: int
    role: str


# ======================================================
# LOGIN (STEP 1 → returns temp_token)
# ======================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    temp_token: str
    next_step: str
    # setup_mfa / verify_mfa / login_mfa


# ======================================================
# VERIFY LOGIN (STEP 2 → returns access_token)
# ======================================================

class VerifyLoginRequest(BaseModel):
    temp_token: str
    code: constr(strip_whitespace=True, min_length=4, max_length=16)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ======================================================
# LOGOUT
# ======================================================

class LogoutRequest(BaseModel):
    session_id: str







