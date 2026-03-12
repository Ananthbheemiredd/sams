from datetime import datetime
from sqlalchemy import (
    Column, String, Float, DateTime,
    ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database.base import Base


class Admission(Base):
    __tablename__ = "admissions"

    # Business Student ID
    admission_id = Column(String(25), primary_key=True)  # STU001

    # From application
    application_id = Column(
        String(20),
        ForeignKey("applications.application_id"),
        nullable=False
    )

    # Org mapping (MANDATORY)
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

    # Student identifiers
    student_roll_no = Column(String(25))  # optional internal roll no

    # Student details
    student_name = Column(String(100))
    student_surname = Column(String(100))

    class_id = Column(
        String(20),
        ForeignKey("classes.class_id"),
        nullable=False
    )
    section_id = Column(
        String(20),
        ForeignKey("sections.section_id"),
        nullable=False
    )

    # Documents (multiple)
    documents = Column(JSON, default=list)
    student_photo = Column(String(255))

    # Exam & fees
    exam_result = Column(String(10))
    paid_amount = Column(Float, default=0.0)

    # Lifecycle status
    status = Column(String(30), default="ACTIVE")
    # ACTIVE / TC / DROPPED / COMPLETED

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    fees = relationship("StudentFee", back_populates="admission")
