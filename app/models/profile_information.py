from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Date, DateTime,
    ForeignKey, JSON, Boolean, Integer
)
from sqlalchemy.orm import relationship
from app.database.base import Base


class ProfileInformation(Base):
    __tablename__ = "profile_information"

    employee_id = Column(Integer, primary_key=True, index=True)

    #  BUSINESS EMPLOYEE CODE (what HR sees)
    employee_code = Column(String(25), unique=True, nullable=False)  # EMP001
    # ======================================================
    # LINK TO LOGIN USER
    # ======================================================
    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=True
    )

    # ======================================================
    # ORG MAPPING (MANDATORY)
    # ======================================================
    school_id = Column(
        String(20),
        ForeignKey("schools.school_id"),
        nullable=False
    )
    branch_id = Column(
        String(20),
        ForeignKey("branches.branch_id"),
        nullable=False
    )

    # ======================================================
    # REPORTING STRUCTURE (SELF FK)
    # ======================================================
    manager_id = Column(
        Integer,
        ForeignKey("profile_information.employee_id"),
        nullable=True
    )

    # ======================================================
    # BASIC INFO
    # ======================================================
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    gender = Column(String(20))
    date_of_birth = Column(Date)
    blood_group = Column(String(5))
    marital_status = Column(String(20))

    # ======================================================
    # CONTACT
    # ======================================================
    email = Column(String(150))
    contact_number = Column(String(20))
    emergency_contact_number = Column(String(20))
    current_address = Column(String(255))
    permanent_address = Column(String(255))

    # ======================================================
    # EMPLOYMENT INFO
    # ======================================================
    designation = Column(String(100))
    department = Column(String(100))
    staff_type = Column(String(100))
    hire_date = Column(Date)
    is_faculty = Column(Boolean, default=False)

    # ======================================================
    # STATUTORY
    # ======================================================
    uan = Column(String(100))
    pan_number = Column(String(10), unique=True)
    aadhaar_number = Column(String(12), unique=True)
    pf_number = Column(String(100))
    esi_number = Column(String(100))

    # ======================================================
    # PAYROLL
    # ======================================================
    annual_ctc = Column(Float)
    bank_name = Column(String(100))
    ifsc_code = Column(String(11))
    account_number = Column(String(32))
    name_of_account_holder = Column(String(100))

    # ======================================================
    # EXPERIENCE & EDUCATION
    # ======================================================
    total_experience = Column(Float)
    employee_experience = Column(JSON, default=list)
    employee_education = Column(JSON, default=list)
    skills = Column(JSON, default=list)

    # ======================================================
    # STATUS & AUDIT
    # ======================================================
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # ======================================================
    # RELATIONSHIPS
    # ======================================================
    user = relationship("User")
    manager = relationship(
        "ProfileInformation",
        remote_side=[employee_id]
    )













