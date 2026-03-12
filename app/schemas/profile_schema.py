# app/schemas/profile_schema.py

from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List


class ProfileInformationCreate(BaseModel):
    # business codes
    employee_code: str
    manager_code: Optional[str] = None  # EMP000 (not int)

    user_id: Optional[int] = None
    school_id: str
    branch_id: str

    first_name: str
    last_name: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    marital_status: Optional[str] = None

    email: Optional[EmailStr] = None
    contact_number: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None

    designation: Optional[str] = None
    department: Optional[str] = None
    staff_type: Optional[str] = None
    hire_date: Optional[date] = None
    is_faculty: Optional[bool] = False

    uan: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pf_number: Optional[str] = None
    esi_number: Optional[str] = None

    annual_ctc: Optional[float] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_number: Optional[str] = None
    name_of_account_holder: Optional[str] = None

    total_experience: Optional[float] = None
    employee_experience: Optional[List] = []
    employee_education: Optional[List] = []
    skills: Optional[List] = []

    is_active: Optional[bool] = True


class ProfileInformationResponse(ProfileInformationCreate):
    employee_id: int

    class Config:
        from_attributes = True
