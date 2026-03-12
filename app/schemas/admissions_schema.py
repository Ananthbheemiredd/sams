from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


# ======================================================
# BASE
# ======================================================

class AdmissionBase(BaseModel):
    student_name: Optional[str] = None
    student_surname: Optional[str] = None

    class_id: str
    section_id: str

    exam_result: Optional[str] = None
    paid_amount: Optional[float] = 0.0

    documents: Optional[List[str]] = None
    student_photo: Optional[str] = None


# ======================================================
# CREATE
# ======================================================

class AdmissionCreate(AdmissionBase):
    application_id: str
    school_id: str
    branch_id: str

    # optional roll no
    student_roll_no: Optional[str] = None


# ======================================================
# UPDATE
# ======================================================

class AdmissionUpdate(BaseModel):
    student_name: Optional[str] = None
    student_surname: Optional[str] = None
    class_id: Optional[str] = None
    section_id: Optional[str] = None

    exam_result: Optional[str] = None
    paid_amount: Optional[float] = None
    status: Optional[str] = None

    documents: Optional[List[str]] = None
    student_photo: Optional[str] = None


# ======================================================
# RESPONSE
# ======================================================

class AdmissionResponse(AdmissionBase):
    admission_id: str
    application_id: str

    school_id: str
    branch_id: str

    student_roll_no: Optional[str] = None
    status: str

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
