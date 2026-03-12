from sqlalchemy import (
    Column, String, Date, DateTime,
    Float, ForeignKey, JSON, func
)
from app.database.base import Base


class Application(Base):
    __tablename__ = "applications"

    # Business PK
    application_id = Column(String(20), primary_key=True)  # APP001

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

    # Student basic info
    full_name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)
    email = Column(String(150), nullable=False)

    # Class applying for
    class_id = Column(
        String(20),
        ForeignKey("classes.class_id"),
        nullable=False
    )

    # Parent details
    father_name = Column(String(100))
    father_occupation = Column(String(100))
    father_phone = Column(String(20))

    mother_name = Column(String(100))
    mother_occupation = Column(String(100))
    mother_phone = Column(String(20))

    guardian_name = Column(String(100))
    guardian_occupation = Column(String(100))
    guardian_phone = Column(String(20))

    # Address
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))

    # Academic history
    previous_school = Column(String(150))

    # Documents / photo (multiple)
    student_photo = Column(String(255))
    documents = Column(JSON, default=list)

    # Tracking
    application_source = Column(String(30), default="DIRECT")
    # DIRECT / PRE_REGISTRATION / WEBSITE / WALKIN

    application_fee = Column(Float, default=0.0)

    status = Column(String(30), default="APPLIED")
    # APPLIED → EXAM_PENDING → EXAM_COMPLETED → SHORTLISTED → REJECTED → ADMITTED

    remarks = Column(String(255))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())








