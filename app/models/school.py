from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class School(Base):
    __tablename__ = "schools"

    school_id = Column(String(20), primary_key=True)  # SCH001

    school_name = Column(String(150), nullable=False)
    code = Column(String(20), unique=True, nullable=False)

    city = Column(String(100))
    state = Column(String(100))
    address = Column(String(255))
    phone = Column(String(20))
    email = Column(String(150))

    is_active = Column(Boolean, server_default="1")
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    branches = relationship("Branch", back_populates="school")















