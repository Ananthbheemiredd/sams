
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    # ======================================================
    # BUSINESS USER ID (PRIMARY KEY)
    # ======================================================
    user_id = Column(Integer, primary_key=True, autoincrement=True) # USR001

    # ======================================================
    # LOGIN IDENTITY
    # ======================================================
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    role_type = Column(String(50), nullable=False)

    # ======================================================
    # ORG MAPPING (VERY IMPORTANT)
    # ======================================================
    school_id = Column(
        String(20),
        ForeignKey("schools.school_id"),
        nullable=True
    )
    branch_id = Column(
        String(20),
        ForeignKey("branches.branch_id"),
        nullable=True
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================
    mfa = relationship("MFASecret", back_populates="user", uselist=False)

    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    user_detail = relationship(
        "UserDetail",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )




