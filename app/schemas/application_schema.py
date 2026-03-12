from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


# ======================================================
# BASE
# ======================================================

class ApplicationBase(BaseModel):
    full_name: str
    surname: str
    dob: date
    gender: str
    email: EmailStr
    grade_level: str

    # Parent / Guardian
    father_name: Optional[str] = None
    father_occupation: Optional[str] = None
    father_phone: Optional[str] = None

    mother_name: Optional[str] = None
    mother_occupation: Optional[str] = None
    mother_phone: Optional[str] = None

    guardian_name: Optional[str] = None
    guardian_occupation: Optional[str] = None
    guardian_phone: Optional[str] = None

    # Address
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    previous_school: Optional[str] = None

    application_fee: float


# ======================================================
# CREATE
# ======================================================

class ApplicationCreate(ApplicationBase):
    school_id: str
    branch_id: str

    # optional uploads
    student_photo: Optional[str] = None
    documents: Optional[str] = None


# ======================================================
# UPDATE
# ======================================================

class ApplicationUpdate(BaseModel):
    full_name: Optional[str] = None
    surname: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    grade_level: Optional[str] = None

    father_name: Optional[str] = None
    father_occupation: Optional[str] = None
    father_phone: Optional[str] = None

    mother_name: Optional[str] = None
    mother_occupation: Optional[str] = None
    mother_phone: Optional[str] = None

    guardian_name: Optional[str] = None
    guardian_occupation: Optional[str] = None
    guardian_phone: Optional[str] = None

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    previous_school: Optional[str] = None

    student_photo: Optional[str] = None
    documents: Optional[str] = None

    status: Optional[str] = None
    remarks: Optional[str] = None


# ======================================================
# RESPONSE
# ======================================================

class ApplicationOut(ApplicationBase):
    application_id: str

    school_id: str
    branch_id: str

    student_photo: Optional[str]
    documents: Optional[str]

    status: str
    remarks: Optional[str]

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
