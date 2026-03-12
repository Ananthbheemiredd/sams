from sqlalchemy import (
    Column, Integer, String, ForeignKey,
    Date, DateTime,LargeBinary
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    student_rollno = Column(String(20), nullable=False)

    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)

    Class = relationship("SchoolClass", back_populates="students")
    section = relationship("Section", back_populates="students")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)








