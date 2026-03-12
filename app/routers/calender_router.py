from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_session
from app.models.academic_calendar import AcademicCalendar
from app.core.auth_dependencies import get_current_user
from app.services.academic_events import emit_event

router = APIRouter(prefix="/academic", tags=["Academic"])

@router.post("/calendar")
async def create_calendar_event(
    title: str,
    event_type: str,
    start_datetime: datetime,
    end_datetime: datetime,
    school_id: str,
    branch_id: str,
    description: str | None = None,
    class_id: str | None = None,
    section_id: str | None = None,
    venue: str | None = None,
    reminder_before_minutes: int = 0,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    event = AcademicCalendar(
        calendar_event_id=f"CAL{int(datetime.utcnow().timestamp())}",
        school_id=school_id,
        branch_id=branch_id,
        event_type=event_type,
        title=title,
        description=description,
        class_id=class_id,
        section_id=section_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        venue=venue,
        reminder_before_minutes=reminder_before_minutes,
    )

    db.add(event)
    await db.commit()

    # 🔔 send notification to students/teachers
    await emit_event(
        event_type="CALENDAR_EVENT_CREATED",
        class_id=class_id or "ALL",
        section_id=section_id or "ALL",
        reference=title,
        actor_id=user["id"],
        db=db,
    )

    return {"message": "Calendar event created"}
