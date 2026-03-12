from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.admissions import Admission

SECTION_LIMIT = 40
SECTIONS = ["A", "B", "C"]


async def assign_section(db: AsyncSession, student_class: str):
    """Automatically allocates the next section based on seat availability."""
    for sec in SECTIONS:
        query = select(Admission).where(
            Admission.student_class == student_class,
            Admission.student_section == sec
        )
        result = await db.execute(query)
        count = len(result.scalars().all())

        if count < SECTION_LIMIT:
            return sec

    raise Exception(f"No seats available for class {student_class}")


async def generate_student_id(db: AsyncSession, cls: str, sec: str):
    """Generates IDs like STD9A0001"""
    prefix = f"STD{cls}{sec}"

    query = select(Admission).where(
        Admission.student_class == cls,
        Admission.student_section == sec
    )
    result = await db.execute(query)
    students = result.scalars().all()

    running_num = len(students) + 1

    return f"{prefix}{running_num:04d}"
