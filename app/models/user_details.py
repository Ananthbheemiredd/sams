from datetime import datetime


from sqlalchemy import (
    Column, String, Date, DateTime,
    ForeignKey, Boolean,Integer
)
from sqlalchemy.orm import relationship
from app.database.base import Base


class UserDetail(Base):
    __tablename__ = "user_details"

    # ======================================================
    # FK TO USERS (PRIMARY KEY)
    # ======================================================
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

    # ======================================================
    # BASIC PROFILE
    # ======================================================
    full_name = Column(String(255), nullable=False)
    gender = Column(String(20))
    phone = Column(String(20))
    address = Column(String(255))
    date_of_birth = Column(Date)
    profile_photo = Column(String(255))

    # ======================================================
    # ROLE IN SYSTEM
    # ======================================================
    role = Column(String(50), nullable=False)
    # ADMIN / FACULTY / PARENT / STAFF / STUDENT

    # ======================================================
    # ORG MAPPING
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
    # OPTIONAL LINKS
    # ======================================================
    employee_code = Column(
        String(25),
        ForeignKey("profile_information.employee_code"),
        nullable=True
    )

    admission_id = Column(
        String(25),
        ForeignKey("admissions.admission_id"),
        nullable=True
    )

    # ======================================================
    # APP / PUSH NOTIFICATIONS
    # ======================================================
    device_token = Column(String(255))

    # ======================================================
    # STATUS & AUDIT
    # ======================================================
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # ======================================================
    # RELATIONSHIPS
    # ======================================================
    user = relationship(
        "User",
        back_populates="user_detail",
        uselist=False
    )


