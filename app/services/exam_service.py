from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.base import get_session
from app.models.exam import StudentExam,Question


async def get_exam_or_404(
    exam_id: int,
    db: AsyncSession = Depends(get_session)
) -> StudentExam:
    exam = await db.get(StudentExam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam





