from sqlalchemy import (
    Column, String, Text,
    DateTime, ForeignKey, Boolean, func
)
from sqlalchemy.orm import relationship
from app.database.base import Base


# ============================================================
# 1) CLASS MASTER
# ============================================================

class Class(Base):
    __tablename__ = "classes"

    class_id = Column(String(20), primary_key=True)  # CLS001
    class_name = Column(String(50), unique=True, nullable=False)


# ============================================================
# 2) SECTION MASTER
# ============================================================

class Section(Base):
    __tablename__ = "sections"

    section_id = Column(String(20), primary_key=True)  # SEC001

    section_name = Column(String(20), nullable=False)

    class_id = Column(
        String(20),
        ForeignKey("classes.class_id"),
        nullable=False
    )

    class_rel = relationship("Class")


# ============================================================
# 3) SUBJECT MASTER
# ============================================================

class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(String(20), primary_key=True)  # SUB001
    subject_name = Column(String(100), unique=True, nullable=False)


# ============================================================
# 4) TEACHER SUBJECT ASSIGNMENT
# ============================================================

class ClassSubjectAssignment(Base):
    __tablename__ = "class_subject_assignments"

    assignment_id = Column(String(25), primary_key=True)  # CSA001

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

    class_id = Column(
        String(20),
        ForeignKey("classes.class_id")
    )
    section_id = Column(
        String(20),
        ForeignKey("sections.section_id")
    )
    subject_id = Column(
        String(20),
        ForeignKey("subjects.subject_id")
    )

    teacher_id = Column(
        String(25),
        ForeignKey("profile_information.employee_code")
    )

    class_rel = relationship("Class")
    section_rel = relationship("Section")
    subject_rel = relationship("Subject")


# ============================================================
# 5) SYLLABUS TRACKING
# ============================================================

class Syllabus(Base):
    __tablename__ = "syllabus"

    syllabus_id = Column(String(25), primary_key=True)  # SYL001

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

    class_id = Column(
        String(20),
        ForeignKey("classes.class_id")
    )
    section_id = Column(
        String(20),
        ForeignKey("sections.section_id")
    )
    subject_id = Column(
        String(20),
        ForeignKey("subjects.subject_id")
    )

    content = Column(Text)

    updated_by = Column(
        String(25),
        ForeignKey("profile_information.employee_code")
    )

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    class_rel = relationship("Class")
    section_rel = relationship("Section")
    subject_rel = relationship("Subject")


# ============================================================
# 6) TEACHING PLAN (Daily / Weekly)
# ============================================================

class TeachingPlan(Base):
    __tablename__ = "teaching_plans"

    teaching_plan_id = Column(String(25), primary_key=True)  # TP001

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

    class_id = Column(
        String(20),
        ForeignKey("classes.class_id")
    )
    section_id = Column(
        String(20),
        ForeignKey("sections.section_id")
    )
    subject_id = Column(
        String(20),
        ForeignKey("subjects.subject_id")
    )

    teacher_id = Column(
        String(25),
        ForeignKey("profile_information.employee_code")
    )

    daily_plan = Column(Text)
    weekly_plan = Column(Text)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    class_rel = relationship("Class")
    section_rel = relationship("Section")
    subject_rel = relationship("Subject")


















