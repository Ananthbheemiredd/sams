from pydantic import BaseModel, EmailStr
from typing import Optional


class PreRegistrationCreate(BaseModel):
    school_id: str
    branch_id: str
    class_id: str   #  IMPORTANT — not class_level

    student_full_name: str
    age: str
    gender: str

    parent_or_guardian_name: str
    relationship: str
    phone_no: str
    email: EmailStr

    address: str
    state: str
    city: Optional[str] = None

    previous_school: Optional[str] = None
    remarks: Optional[str] = None

class PreRegistrationResponse(PreRegistrationCreate):
    pre_registration_id: str
    status: str

    class Config:
        from_attributes = True
