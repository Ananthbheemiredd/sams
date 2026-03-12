# app/schemas/fee_schema.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# -------------------------------------------------
# CREATE STUDENT FEE
# -------------------------------------------------
class StudentFeeCreate(BaseModel):
    admission_id: str
    fee_type_id: str
    amount: float
    discount: float = 0.0
    discount_reason: Optional[str] = None


# -------------------------------------------------
# UPDATE STUDENT FEE
# -------------------------------------------------
class StudentFeeUpdate(BaseModel):
    amount: Optional[float] = None
    discount: Optional[float] = None
    discount_reason: Optional[str] = None
    status: Optional[str] = None


# -------------------------------------------------
# PAY FEE
# -------------------------------------------------
class StudentFeePayment(BaseModel):
    amount: float


# -------------------------------------------------
# RESPONSE
# -------------------------------------------------
class StudentFeeResponse(BaseModel):
    student_fee_id: str
    admission_id: str
    fee_type_id: str

    amount: float
    discount: float
    paid_fee: float
    pending_fee: float
    status: str

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
