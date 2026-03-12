from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.database.base import Base


class Branch(Base):
    __tablename__ = "branches"


    branch_id = Column(String(20), primary_key=True)  # BR001
    school_id = Column(String(20), ForeignKey("schools.school_id"))

    branch_name = Column(String(150), nullable=False)
    branch_code = Column(String(50), unique=True, nullable=False)

    city = Column(String(100), nullable=False)
    address = Column(String(255))
    phone = Column(String(20))
    email = Column(String(150))

    is_active = Column(Boolean, server_default="1")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship
    school = relationship("School", back_populates="branches")


