from sqlalchemy import (
    Column, String, Float,
    DateTime, ForeignKey, Boolean, func
)
from sqlalchemy.orm import relationship
from app.database.base import Base


# ============================================================
# 1) FEE MASTER (Defined once by admin)
# ============================================================

class FeeMaster(Base):
    __tablename__ = "fee_master"

    fee_type_id = Column(String(20), primary_key=True)  # FEE001
    fee_type = Column(String(100), unique=True, nullable=False)

    is_optional = Column(Boolean, default=False)
    is_hostel_related = Column(Boolean, default=False)


# ============================================================
# 2) STUDENT FEES (Per student per fee type)
# ============================================================

class StudentFee(Base):
    __tablename__ = "student_fees"

    student_fee_id = Column(String(25), primary_key=True)  # STF001

    # Org mapping (IMPORTANT)
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

    # Student mapping
    admission_id = Column(
        String(25),
        ForeignKey("admissions.admission_id", ondelete="CASCADE"),
        nullable=False
    )

    # Fee type
    fee_type_id = Column(
        String(20),
        ForeignKey("fee_master.fee_type_id"),
        nullable=False
    )

    # Optional hostel link
    hostel_allocation_id = Column(
        String(25),
        ForeignKey("hostel_allocations.hostel_allocation_id"),
        nullable=True
    )

    # Amounts
    amount = Column(Float, default=0)
    discount = Column(Float, default=0)
    discount_reason = Column(String(255))

    paid_fee = Column(Float, default=0)
    pending_fee = Column(Float, default=0)

    status = Column(String(20), default="UNPAID")
    # UNPAID / PARTIAL / PAID

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    admission = relationship("Admission", back_populates="fees")
    fee_master = relationship("FeeMaster")








