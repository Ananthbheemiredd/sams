from sqlalchemy import (
    Column, String, Integer, Float,
    DateTime, ForeignKey, LargeBinary, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base
from datetime import datetime


# =========================================================
# SALARY BREAKUP  ← USED BY ROUTER + SCHEMA
# =========================================================

class Salary_components(Base):
    __tablename__ = "salary_breakup"

    # FK to profile_information.employee_id (INTEGER)
    emp_id = Column(
        Integer,
        ForeignKey("profile_information.employee_id"),
        primary_key=True,
    )

    annual_ctc = Column(Float, nullable=False)
    regime = Column(String(50), default="new")

    monthly_ctc = Column(Float)
    basic_salary = Column(Float)
    hra = Column(Float)
    food_allowance = Column(Float)
    special_allowance = Column(Float)
    other_allowance = Column(Float)

    pf_employee = Column(Float)
    pf_employer = Column(Float)
    professional_tax = Column(Float)
    tax_deductions = Column(Float)
    health_insurance = Column(Float)

    total_ctc = Column(Float)
    net_salary = Column(Float)

    employee = relationship("ProfileInformation")


# =========================================================
# SALARY POLICY (JSON BASED)
# =========================================================

class SalaryPolicy1(Base):
    __tablename__ = "salary_policy1"

    id = Column(Integer, primary_key=True, index=True)
    salary_sheet_id = Column(String(50), unique=True, nullable=False)

    effective_from = Column(DateTime, nullable=False)
    is_active = Column(Integer, default=1)

    salary_range = Column(JSON, nullable=False)
    components = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# =========================================================
# TAX SLABS (JSON LIST)
# =========================================================

class TaxSlab1(Base):
    __tablename__ = "tax_slabs1"

    id = Column(Integer, primary_key=True, index=True)
    slab_id = Column(String(20), unique=True, index=True)

    regime = Column(String(50), nullable=False)

    slab_ranges = Column(JSON, nullable=False)

    effective_from = Column(DateTime, nullable=False)
    is_active = Column(Integer, default=1)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
