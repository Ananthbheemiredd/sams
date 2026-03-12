from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


# ============================================================
# 1) EXAM PAPER
# ============================================================

class ExamPaper(Base):
    __tablename__ = "exam_papers"

    paper_id = Column(String(25), primary_key=True)  # EXAM001

    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False)
    class_level = Column(String(20), nullable=False)
    difficulty = Column(String(20), nullable=False)

    file_path = Column(String(255), nullable=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    questions = relationship(
        "Question",
        back_populates="paper",
        cascade="all, delete-orphan"
    )


# ============================================================
# 2) QUESTIONS
# ============================================================

class Question(Base):
    __tablename__ = "questions"

    question_id = Column(String(25), primary_key=True)  # Q001

    paper_id = Column(
        String(25),
        ForeignKey("exam_papers.paper_id", ondelete="CASCADE"),
        nullable=False
    )

    question_text = Column(String(500), nullable=False)

    option_a = Column(String(255), nullable=False)
    option_b = Column(String(255), nullable=False)
    option_c = Column(String(255), nullable=False)
    option_d = Column(String(255), nullable=False)

    correct_option = Column(String(5), nullable=False)

    paper = relationship("ExamPaper", back_populates="questions")


# ============================================================
# 3) STUDENT EXAM ATTEMPT
# ============================================================

class StudentExam(Base):
    __tablename__ = "student_exams"

    student_exam_id = Column(String(25), primary_key=True)  # STEX001

    application_id = Column(
        String(20),
        ForeignKey("applications.application_id", ondelete="CASCADE"),
        nullable=False
    )

    paper_id = Column(
        String(25),
        ForeignKey("exam_papers.paper_id"),
        nullable=False
    )

    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)

    score = Column(Integer, default=0)
    result = Column(String(20), default="PENDING")

    paper = relationship("ExamPaper")
    answers = relationship(
        "StudentAnswer",
        back_populates="exam",
        cascade="all, delete-orphan"
    )


# ============================================================
# 4) STUDENT ANSWERS
# ============================================================

class StudentAnswer(Base):
    __tablename__ = "student_answers"

    answer_id = Column(String(25), primary_key=True)  # ANS001

    student_exam_id = Column(
        String(25),
        ForeignKey("student_exams.student_exam_id", ondelete="CASCADE"),
        nullable=False
    )

    question_id = Column(
        String(25),
        ForeignKey("questions.question_id"),
        nullable=False
    )

    selected_option = Column(String(5))
    is_correct = Column(Integer)

    exam = relationship("StudentExam", back_populates="answers")
    question = relationship("Question")
