from sqlalchemy import (
    Column, String, Boolean, DateTime,
    Integer, JSON, func, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database.base import Base
import uuid


class MFASecret(Base):
    __tablename__ = "mfa_secrets"

    # Internal technical PK (UUID)
    id = Column(
        String(50),
        primary_key=True,
        default=lambda: uuid.uuid4().hex
    )

    # ======================================================
    # FK TO USER (BUSINESS KEY)
    # ======================================================
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role_type = Column(String(50), nullable=False, index=True)

    secret_key = Column(String(128))

    is_verified = Column(Boolean, default=False)

    enrolled_at = Column(DateTime)
    last_verified_at = Column(DateTime)
    last_rotated_at = Column(DateTime)

    # Security controls
    backup_codes = Column(JSON, default=list)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="mfa")
