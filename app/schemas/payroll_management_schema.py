from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date, datetime

# =========================================================
# SALARY BREAKUP
# =========================================================

class salryenter(BaseModel):
    emp_id: int
    annual_ctc: float
    regime: str = "new"


class SalaryInput(BaseModel):
    emp_id: int
    annual_ctc: float
    regime: str

    monthly_ctc: Optional[float] = 0.0
    basic_salary: Optional[float] = 0.0
    hra: Optional[float] = 0.0
    food_allowance: Optional[float] = 0.0
    special_allowance: Optional[float] = 0.0
    other_allowance: Optional[float] = 0.0
    pf_employee: Optional[float] = 0.0
    pf_employer: Optional[float] = 0.0
    professional_tax: Optional[float] = 0.0
    tax_deductions: Optional[float] = 0.0
    health_insurance: Optional[float] = 0.0
    total_ctc: Optional[float] = 0.0
    net_salary: Optional[float] = 0.0

    model_config = {"from_attributes": True}


# =========================================================
# SALARY POLICY
# =========================================================

class SalaryRangeSchema(BaseModel):
    min_annual_ctc: int = Field(..., example=500000)
    max_annual_ctc: int = Field(..., example=800000)
    currency: str = Field(default="INR")


class SalaryComponentSchema(BaseModel):
    component_name: str
    percentage: Optional[float] = None
    amount: Optional[float] = None
    type: Literal["earning", "deduction"]
    calculation_type: Literal["percentage", "fixed"]


class SalaryPolicyCreateSchema(BaseModel):
    effective_from: date
    is_active: bool = True
    salary_range: SalaryRangeSchema
    components: List[SalaryComponentSchema]


class SalaryPolicyUpdateSchema(BaseModel):
    effective_from: Optional[date] = None
    is_active: Optional[bool] = None
    salary_range: Optional[SalaryRangeSchema] = None
    components: Optional[List[SalaryComponentSchema]] = None


class SalaryPolicyResponseSchema(SalaryPolicyCreateSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PolicyComponentPatchSchema(BaseModel):
    percentage: Optional[float] = None
    amount: Optional[float] = None
    calculation_type: Optional[Literal["percentage", "fixed"]] = None
    type: Optional[Literal["earning", "deduction"]] = None


# =========================================================
# TAX SLABS (MATCHES TaxSlab1 JSON STRUCTURE)
# =========================================================

class SlabRangeSchema(BaseModel):
    lower_limit: float
    upper_limit: float
    rate: float


class TaxSlabCreateSchema(BaseModel):
    regime: str
    slab_ranges: List[SlabRangeSchema]
    effective_from: date
    is_active: Optional[int] = 1


class TaxSlabUpdateSchema(BaseModel):
    regime: Optional[str] = None
    slab_ranges: Optional[List[SlabRangeSchema]] = None
    effective_from: Optional[date] = None
    is_active: Optional[int] = None


class TaxSlabResponseSchema(BaseModel):
    id: int
    slab_id: str
    regime: str
    slab_ranges: List[SlabRangeSchema]
    effective_from: date
    is_active: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
