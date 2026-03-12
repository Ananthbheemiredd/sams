from sqlalchemy import (
    Column, String, DateTime,
    Text, ForeignKey, Boolean, Integer, func
)
from app.database.base import Base


class AcademicCalendar(Base):
    __tablename__ = "academic_calendar"

    calendar_event_id = Column(String(25), primary_key=True)  # CAL001

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
    # EVENT DETAILS
    # ======================================================
    event_type = Column(String(50), nullable=False)
    # HOLIDAY | EXAM | EVENT | ACTIVITY | MEETING

    title = Column(String(200), nullable=False)
    description = Column(Text)
    venue = Column(String(255))

    # ======================================================
    # TARGET AUDIENCE (OPTIONAL)
    # ======================================================
    class_id = Column(
        String(20),
        ForeignKey("classes.class_id"),
        nullable=True
    )
    section_id = Column(
        String(20),
        ForeignKey("sections.section_id"),
        nullable=True
    )

    # If NULL → whole school
    is_school_wide = Column(Boolean, default=True)

    # ======================================================
    # TIMING
    # ======================================================
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)

    # ======================================================
    # REMINDER ENGINE SUPPORT
    # ======================================================
    reminder_before_minutes = Column(Integer, default=0)
    reminder_sent = Column(Boolean, default=False)

    # ======================================================
    # STATUS & AUDIT
    # ======================================================
    is_active = Column(Boolean, default=True)

    created_by = Column(String(25))  # employee_code
    updated_by = Column(String(25))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
