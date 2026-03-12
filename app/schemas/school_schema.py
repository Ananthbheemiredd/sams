from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ======================================================
# CREATE
# ======================================================

class SchoolCreate(BaseModel):
    school_name: str
    code: str
    city: str
    state: str
    address: str
    phone: str
    email: EmailStr


# ======================================================
# UPDATE
# ======================================================

class SchoolUpdate(BaseModel):
    school_name: Optional[str] = None
    school_city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


# ======================================================
# RESPONSE
# ======================================================

class SchoolResponse(BaseModel):
    school_id: str

    school_name: str
    code: str
    city: str
    state: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]

    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
