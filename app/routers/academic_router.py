from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.base import get_session
from app.models.academic import (
    ClassSubjectAssignment,
    Syllabus,
    TeachingPlan,
)
from app.models.academic_calendar import AcademicCalendar
from app.schemas.academic_schema import (
    AssignmentCreate,
    SyllabusCreate,
    TeachingPlanCreate,
    CalendarCreate,
)
from app.notification.notification_service import notify_user

router = APIRouter(prefix="/academic", tags=["Academic"])


# ============================================================
# HELPER → NOTIFY ASSIGNED TEACHER
# ============================================================
async def notify_assigned_teacher(
    *,
    db: AsyncSession,
    class_id: int,
    section_id: int,
    subject_id: int,
    actor_id: int | None,
    message: str,
):
    result = await db.execute(
        select(ClassSubjectAssignment).where(
            ClassSubjectAssignment.class_id == class_id,
            ClassSubjectAssignment.section_id == section_id,
            ClassSubjectAssignment.subject_id == subject_id,
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        return

    # Do not notify same teacher
    if actor_id and assignment.teacher_id == actor_id:
        return

    await notify_user(
        db=db,
        user_id=assignment.teacher_id,
        role="TEACHER",
        module="ACADEMIC",
        title="Academic Update",
        message=message,
        data={
            "class_id": class_id,
            "section_id": section_id,
            "subject_id": subject_id,
        },
    )


# ============================================================
# ASSIGN TEACHER TO SUBJECT
# ============================================================
@router.post("/assign")
async def create_assignment(
    payload: AssignmentCreate,
    db: AsyncSession = Depends(get_session),
):
    obj = ClassSubjectAssignment(**payload.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    await notify_user(
        db=db,
        user_id=obj.teacher_id,
        role="TEACHER",
        module="ACADEMIC",
        title="New Subject Assigned",
        message="You have been assigned a new class/subject",
        data=payload.dict(),
    )

    return obj


@router.get("/assign")
async def list_assignments(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ClassSubjectAssignment))
    return result.scalars().all()


@router.delete("/assign/{assignment_id}")
async def delete_assignment(assignment_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(ClassSubjectAssignment).where(
            ClassSubjectAssignment.id == assignment_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Assignment not found")

    await db.delete(obj)
    await db.commit()
    return {"status": "deleted"}


# ============================================================
# SYLLABUS
# ============================================================
@router.post("/syllabus")
async def create_syllabus(
    payload: SyllabusCreate,
    db: AsyncSession = Depends(get_session),
):
    obj = Syllabus(**payload.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    await notify_assigned_teacher(
        db=db,
        class_id=obj.class_id,
        section_id=obj.section_id,
        subject_id=obj.subject_id,
        actor_id=None,
        message="Syllabus Updated",
    )

    return obj


@router.get("/syllabus")
async def list_syllabus(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Syllabus))
    return result.scalars().all()


@router.patch("/syllabus/{syllabus_id}")
async def update_syllabus(
    syllabus_id: int,
    payload: SyllabusCreate,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Syllabus).where(Syllabus.id == syllabus_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Syllabus not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)

    await notify_assigned_teacher(
        db=db,
        class_id=obj.class_id,
        section_id=obj.section_id,
        subject_id=obj.subject_id,
        actor_id=None,
        message="Syllabus Updated",
    )

    return obj


@router.delete("/syllabus/{syllabus_id}")
async def delete_syllabus(syllabus_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Syllabus).where(Syllabus.id == syllabus_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Syllabus not found")

    await db.delete(obj)
    await db.commit()
    return {"status": "deleted"}


# ============================================================
# TEACHING PLAN
# ============================================================
@router.post("/teaching-plan")
async def create_plan(
    payload: TeachingPlanCreate,
    db: AsyncSession = Depends(get_session),
):
    obj = TeachingPlan(**payload.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    await notify_assigned_teacher(
        db=db,
        class_id=obj.class_id,
        section_id=obj.section_id,
        subject_id=obj.subject_id,
        actor_id=obj.teacher_id,
        message="Teaching Plan Updated",
    )

    return obj


@router.get("/teaching-plan")
async def list_plans(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(TeachingPlan))
    return result.scalars().all()


@router.patch("/teaching-plan/{plan_id}")
async def update_plan(
    plan_id: int,
    payload: TeachingPlanCreate,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(TeachingPlan).where(TeachingPlan.id == plan_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Plan not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)

    await notify_assigned_teacher(
        db=db,
        class_id=obj.class_id,
        section_id=obj.section_id,
        subject_id=obj.subject_id,
        actor_id=obj.teacher_id,
        message="Teaching Plan Updated",
    )

    return obj


@router.delete("/teaching-plan/{plan_id}")
async def delete_plan(plan_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(TeachingPlan).where(TeachingPlan.id == plan_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Plan not found")

    await db.delete(obj)
    await db.commit()
    return {"status": "deleted"}


# ============================================================
# ACADEMIC CALENDAR
# ============================================================
@router.post("/calendar")
async def create_event(
    payload: CalendarCreate,
    db: AsyncSession = Depends(get_session),
):
    obj = AcademicCalendar(**payload.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    return obj


@router.get("/calendar")
async def list_events(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(AcademicCalendar))
    return result.scalars().all()


@router.delete("/calendar/{event_id}")
async def delete_event(
    event_id: str,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(AcademicCalendar).where(
            AcademicCalendar.calendar_event_id == event_id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Event not found")

    await db.delete(obj)
    await db.commit()
    return {"status": "deleted"}











