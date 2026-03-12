from sqlalchemy import (
    Column, String, DateTime,
    ForeignKey, func
)
from app.database.base import Base


class PreRegistration(Base):
    __tablename__ = "pre_registrations"

    # Business Lead ID
    pre_registration_id = Column(String(25), primary_key=True)  # PR001

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
    # STUDENT BASIC INFO (LEAD)
    # ======================================================
    student_full_name = Column(String(150), nullable=False)
    age = Column(String(10), nullable=False)
    gender = Column(String(10), nullable=False)

    class_id = Column(
        String(20),
        ForeignKey("classes.class_id"),
        nullable=False
    )

    # ======================================================
    # PARENT INFO
    # ======================================================
    parent_or_guardian_name = Column(String(150), nullable=False)
    relationship = Column(String(50), nullable=False)
    phone_no = Column(String(20), nullable=False)
    email = Column(String(150), nullable=False)

    # ======================================================
    # ADDRESS
    # ======================================================
    address = Column(String(255), nullable=False)
    state = Column(String(100), nullable=False)
    city = Column(String(100))

    # ======================================================
    # ACADEMIC HISTORY
    # ======================================================
    previous_school = Column(String(200))

    # ======================================================
    # LEAD TRACKING
    # ======================================================
    status = Column(String(30), default="NEW")
    # NEW → CONTACTED → VISITED → CONVERTED → REJECTED

    remarks = Column(String(255))

    created_at = Column(DateTime, server_default=func.now())










