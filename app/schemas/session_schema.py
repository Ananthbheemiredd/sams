from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ======================================================
# CREATE (backend creates session_id)
# ======================================================

class UserSessionCreate(BaseModel):
    user_id: int
    role_type: str
    device_type: Optional[str] = None
    device_name: Optional[str] = None
    ip_address: Optional[str] = None


# ======================================================
# RESPONSE
# ======================================================

class UserSessionResponse(BaseModel):
    session_id: str
    user_id: int
    role_type: str

    jwt_token: Optional[str] = None

    device_type: Optional[str] = None
    device_name: Optional[str] = None
    ip_address: Optional[str] = None

    login_time: datetime
    expires_at: Optional[datetime] = None
    logout_time: Optional[datetime] = None

    is_active: bool

    class Config:
        from_attributes = True
