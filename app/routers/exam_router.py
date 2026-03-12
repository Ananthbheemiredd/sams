from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.base import get_session
from app.models.exam import ExamPaper, Question, StudentExam, StudentAnswer
from app.models.application_form import Application
from app.utils.s3_utils import upload_to_s3

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.post("/paper")
async def upload_exam_paper(
    title: str,
    subject: str,
    class_level: str,
    difficulty: str,
    start_time: datetime,
    end_time: datetime,
    duration_minutes: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
):
    s3_path = await upload_to_s3(file, folder="exam-papers")

    paper = ExamPaper(
        paper_id=f"PAPER{int(datetime.utcnow().timestamp())}",
        title=title,
        subject=subject,
        class_level=class_level,
        difficulty=difficulty,
        file_path=s3_path,
        start_time=start_time,
        end_time=end_time,
        duration_minutes=duration_minutes,
    )

    db.add(paper)
    await db.commit()
    return {"paper_id": paper.paper_id}

@router.post("/{paper_id}/questions")
async def add_questions(
    paper_id: str,
    questions: list[dict],
    db: AsyncSession = Depends(get_session),
):
    for q in questions:
        question = Question(
            question_id=f"Q{int(datetime.utcnow().timestamp())}",
            paper_id=paper_id,
            question_text=q["question_text"],
            option_a=q["a"],
            option_b=q["b"],
            option_c=q["c"],
            option_d=q["d"],
            correct_option=q["correct"],
        )
        db.add(question)

    await db.commit()
    return {"message": "Questions added"}

@router.post("/start/{paper_id}")
async def start_exam(
    paper_id: str,
    application_id: str,
    db: AsyncSession = Depends(get_session),
):
    exam = StudentExam(
        student_exam_id=f"EXAM{int(datetime.utcnow().timestamp())}",
        application_id=application_id,
        paper_id=paper_id,
        started_at=datetime.utcnow(),
    )
    db.add(exam)
    await db.commit()
    return {"student_exam_id": exam.student_exam_id}

@router.post("/{student_exam_id}/submit")
async def submit_exam(
    student_exam_id: str,
    answers: dict[str, str],
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(StudentExam).where(
            StudentExam.student_exam_id == student_exam_id
        )
    )
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(404, "Exam not found")

    score = 0

    for qid, selected in answers.items():
        qres = await db.execute(
            select(Question).where(Question.question_id == qid)
        )
        question = qres.scalar_one()

        is_correct = selected == question.correct_option
        if is_correct:
            score += 1

        db.add(
            StudentAnswer(
                exam_id=student_exam_id,
                question_id=qid,
                selected_option=selected,
                is_correct=is_correct,
            )
        )

    exam.score = score
    exam.result = "PASS" if score >= 40 else "FAIL"
    exam.completed_at = datetime.utcnow()

    await db.commit()
    return {"score": score, "result": exam.result}

@router.post("/{student_exam_id}/upload-document")
async def upload_exam_document(
    student_exam_id: str,
    file: UploadFile = File(...),
):
    s3_path = await upload_to_s3(file, folder="exam-documents")
    return {
        "student_exam_id": student_exam_id,
        "document_path": s3_path,
    }



