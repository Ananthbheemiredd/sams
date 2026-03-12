# =====================================================================================
# PAYROLL SCHEMAS – SAMS (FINAL MERGED VERSION)
# =====================================================================================

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import date, datetime
from enum import Enum


# =====================================================================================
# ENUMS
# =====================================================================================

class ArrearTypeEnum(str, Enum):
    SALARY_REVISION = "salary_revision"
    APPRAISAL = "appraisal"


class BonusTypeEnum(str, Enum):
    FESTIVAL = "festival"
    REFERRAL = "referral"
    OTHER = "other"


class ExpenseTypeEnum(str, Enum):
    TRAVELEXPENSE = "travelexpense"
    FOODEXPENSE = "foodexpense"
    WIFIBILL = "wifibill"
    HEALTHINSURENSE = "healthinsurense"


# =====================================================================================
# NOTIFICATION
# =====================================================================================

class NotificationStructure(BaseModel):
    scenario: Optional[str] = None
    data: Optional[dict] = None
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# =====================================================================================
# EMPLOYEE PROFILE (PAYROLL VIEW)
# =====================================================================================

class ProfileInformationBase(BaseModel):
    employee_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    designation_id: Optional[str] = None
    is_active: Optional[int] = 1


class ProfileInformationRead(ProfileInformationBase):
    email: Optional[Dict] = None
    contact_number: Optional[Dict] = None
    emergency_contact_number: Optional[Dict] = None
    skills: Optional[Dict] = None

    annual_ctc: Optional[float] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pf_number: Optional[str] = None

    model_config = {"from_attributes": True}


# =====================================================================================
# SALARY INPUT / RESULT
# =====================================================================================

class SalaryEnter(BaseModel):
    emp_id: str
    annual_ctc: float
    regime: Optional[str] = "new"


class SalaryComponentBase(BaseModel):
    emp_id: str
    annual_ctc: float
    regime: Optional[str] = "new"

    monthly_ctc: Optional[float] = None
    basic_salary: Optional[float] = None
    hra: Optional[float] = None
    food_allowance: Optional[float] = None
    special_allowance: Optional[float] = None
    other_allowance: Optional[float] = None

    pf_employee: Optional[float] = None
    pf_employer: Optional[float] = None
    professional_tax: Optional[float] = None
    health_insurance: Optional[float] = None

    total_ctc: Optional[float] = None
    net_salary: Optional[float] = None


class SalaryInput(SalaryComponentBase):
    model_config = {"from_attributes": True}


# =====================================================================================
# PAYSLIP
# =====================================================================================

class PayslipRead(BaseModel):
    emp_id: str
    year: int
    month: int
    filename: str
    status: str
    approved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PayslipActionRead(BaseModel):
    emp_id: str
    filename: str
    action_type: str
    timestamp: datetime

    model_config = {"from_attributes": True}


# =====================================================================================
# ARREARS
# =====================================================================================

class ArrearBase(BaseModel):
    employee_id: str
    month: int
    year: int
    amount: float
    type: ArrearTypeEnum
    reason: Optional[str] = None


class ArrearRead(ArrearBase):
    id: int
    model_config = {"from_attributes": True}


# =====================================================================================
# BONUS
# =====================================================================================

class BonusBase(BaseModel):
    employee_id: str
    month: int
    year: int
    amount: float
    type: BonusTypeEnum
    remarks: Optional[str] = None


class BonusRead(BonusBase):
    id: int
    model_config = {"from_attributes": True}


# =====================================================================================
# EXPENSE CLAIMS
# =====================================================================================

class ExpenseClaimBase(BaseModel):
    employee_id: str
    expenses_type: ExpenseTypeEnum
    bill_number: str
    amount: float
    description: Optional[str] = None


class ExpenseClaimRead(ExpenseClaimBase):
    id: int
    model_config = {"from_attributes": True}


# =====================================================================================
# PAYROLL CYCLE
# =====================================================================================

class PayrollCycleRead(BaseModel):
    id: int
    year: int
    month: int
    approval_status: str
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    model_config = {"from_attributes": True}


# =====================================================================================
# SALARY POLICY
# =====================================================================================

class SalaryRangeSchema(BaseModel):
    min_annual_ctc: float
    max_annual_ctc: float
    currency: str = "INR"


class SalaryComponentPolicySchema(BaseModel):
    component_name: str
    percentage: Optional[float] = None
    amount: Optional[float] = None
    type: Literal["earning", "deduction"]
    calculation_type: Literal["percentage", "fixed"]


class SalaryPolicyCreateSchema(BaseModel):
    effective_from: date
    is_active: bool = True
    salary_range: SalaryRangeSchema
    components: List[SalaryComponentPolicySchema]


class SalaryPolicyUpdateSchema(BaseModel):
    effective_from: Optional[date] = None
    is_active: Optional[bool] = None
    salary_range: Optional[SalaryRangeSchema] = None
    components: Optional[List[SalaryComponentPolicySchema]] = None


class SalaryPolicyResponseSchema(BaseModel):
    id: int
    salary_sheet_id: str
    effective_from: date
    is_active: bool
    salary_range: Dict
    components: List[Dict]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# =====================================================================================
# TAX SLABS (NEW STRUCTURE – USED BY UTILS)
# =====================================================================================

class TaxSlabRangeSchema(BaseModel):
    lower_limit: float
    upper_limit: float
    rate: float


class TaxSlabCreateSchema(BaseModel):
    regime: str
    slab_ranges: List[TaxSlabRangeSchema]
    effective_from: date
    is_active: bool = True


class TaxSlabUpdateSchema(BaseModel):
    regime: Optional[str] = None
    slab_ranges: Optional[List[TaxSlabRangeSchema]] = None
    effective_from: Optional[date] = None
    is_active: Optional[bool] = None


class TaxSlabResponseSchema(BaseModel):
    id: int
    slab_id: str
    regime: str
    slab_ranges: List[Dict]
    effective_from: date
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
