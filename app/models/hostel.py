from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime,
    ForeignKey, Integer
)
from sqlalchemy.orm import relationship
from app.database.base import Base


# ============================================================
# 1) HOSTEL MASTER
# ============================================================

class Hostel(Base):
    __tablename__ = "hostels"

    hostel_id = Column(String(25), primary_key=True)  # HST001

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

    hostel_name = Column(String(100), nullable=False)
    gender_type = Column(String(20))  # Boys / Girls
    warden_name = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)

    rooms = relationship(
        "HostelRoom",
        back_populates="hostel",
        cascade="all, delete-orphan"
    )


# ============================================================
# 2) ROOMS
# ============================================================

class HostelRoom(Base):
    __tablename__ = "hostel_rooms"

    room_id = Column(String(25), primary_key=True)  # RM001

    hostel_id = Column(
        String(25),
        ForeignKey("hostels.hostel_id", ondelete="CASCADE"),
        nullable=False
    )

    floor_number = Column(Integer, nullable=False)
    room_number = Column(String(20), nullable=False)
    total_beds = Column(Integer, nullable=False)

    hostel = relationship("Hostel", back_populates="rooms")

    allocations = relationship(
        "HostelAllocation",
        back_populates="room",
        cascade="all, delete-orphan"
    )


# ============================================================
# 3) STUDENT HOSTEL ALLOCATION
# ============================================================

class HostelAllocation(Base):
    __tablename__ = "hostel_allocations"

    hostel_allocation_id = Column(String(25), primary_key=True)  # HAL001

    admission_id = Column(
        String(25),
        ForeignKey("admissions.admission_id", ondelete="CASCADE"),
        nullable=False
    )

    room_id = Column(
        String(25),
        ForeignKey("hostel_rooms.room_id", ondelete="CASCADE"),
        nullable=False
    )

    bed_no = Column(Integer, nullable=False)

    allocated_on = Column(DateTime, default=datetime.utcnow)
    vacated_on = Column(DateTime, nullable=True)

    status = Column(String(20), default="ACTIVE")

    room = relationship("HostelRoom", back_populates="allocations")
    admission = relationship("Admission")












