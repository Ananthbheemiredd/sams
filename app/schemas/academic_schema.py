from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ============================================================
# TEACHER ASSIGNMENT
# ============================================================
class AssignmentCreate(BaseModel):
    class_id: int
    section_id: int
    subject_id: int
    teacher_id: int
    school_id: int
    branch_id: int


# ============================================================
# SYLLABUS
# ============================================================
class SyllabusCreate(BaseModel):
    class_id: int
    section_id: int
    subject_id: int
    content: str
    school_id: int
    branch_id: int


# ============================================================
# TEACHING PLAN
# ============================================================
class TeachingPlanCreate(BaseModel):
    class_id: int
    section_id: int
    subject_id: int
    teacher_id: int
    daily_plan: str
    weekly_plan: str
    school_id: int
    branch_id: int


# ============================================================
# ACADEMIC CALENDAR
# ============================================================
class CalendarCreate(BaseModel):
    school_id: int
    branch_id: int

    event_type: str
    title: str
    description: Optional[str] = None

    class_id: Optional[int] = None
    section_id: Optional[int] = None

    start_datetime: datetime
    end_datetime: datetime

    venue: Optional[str] = None
    reminder_before_minutes: Optional[int] = 0


class CalendarResponse(CalendarCreate):
    calendar_event_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
