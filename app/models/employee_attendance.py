

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date, String

from app.database.base import Base


class TeacherAttendance(Base):
    __tablename__ = "teacher_attendance"

    id = Column(Integer, primary_key=True, index=True)

    teacher_id = Column(Integer, ForeignKey("profile_information.Employee_id"), nullable=False)

    date = Column(Date, nullable=False)

    time_in = Column(DateTime, nullable=True)
    time_out = Column(DateTime, nullable=True)

    status = Column(String(20), nullable=False)
    # PRESENT | ABSENT | HALF_DAY | LEAVE

    geo_location = Column(String(255), nullable=True)
    face_id = Column(String(255), nullable=True)





