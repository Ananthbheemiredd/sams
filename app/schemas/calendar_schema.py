from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ======================================================
# BASE
# ======================================================

class AcademicCalendarBase(BaseModel):
    school_id: str
    branch_id: str

    event_type: str  # HOLIDAY | EXAM | EVENT | ACTIVITY | MEETING

    title: str
    description: Optional[str] = None

    class_id: Optional[str] = None
    section_id: Optional[str] = None

    start_datetime: datetime
    end_datetime: datetime

    venue: Optional[str] = None
    reminder_before_minutes: int = 0


# ======================================================
# CREATE
# ======================================================

class AcademicCalendarCreate(AcademicCalendarBase):
    pass


# ======================================================
# UPDATE
# ======================================================

class AcademicCalendarUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None

    class_id: Optional[str] = None
    section_id: Optional[str] = None

    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

    venue: Optional[str] = None
    reminder_before_minutes: Optional[int] = None
    is_active: Optional[bool] = None


# ======================================================
# RESPONSE
# ======================================================

class AcademicCalendarResponse(AcademicCalendarBase):
    calendar_event_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
