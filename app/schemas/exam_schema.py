from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


# ======================================================
# QUESTION RESPONSE (from Question table)
# ======================================================

class QuestionOut(BaseModel):
    question_id: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attributes = True


# ======================================================
# EXAM PAPER RESPONSE
# ======================================================

class ExamPaperOut(BaseModel):
    paper_id: str
    title: str
    subject: str
    class_level: str
    difficulty: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int

    class Config:
        from_attributes = True


# ======================================================
# CREATE STUDENT EXAM (when student starts exam)
# ======================================================

class StudentExamCreate(BaseModel):
    application_id: str
    paper_id: str


# ======================================================
# SUBMIT ANSWERS
# ======================================================

class StudentAnswerSubmit(BaseModel):
    question_id: str
    selected_option: str


class StudentExamSubmit(BaseModel):
    answers: List[StudentAnswerSubmit]


# ======================================================
# STUDENT EXAM RESPONSE (full exam view)
# ======================================================

class StudentExamResponse(BaseModel):
    student_exam_id: str
    application_id: str
    paper: ExamPaperOut
    questions: List[QuestionOut]

    started_at: datetime
    completed_at: Optional[datetime]
    score: int
    result: str

    class Config:
        from_attributes = True
