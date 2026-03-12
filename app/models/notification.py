from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    DateTime,
    ForeignKey,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship
from app.database.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    # SINGLE PRIMARY KEY
    notification_id = Column(Integer, primary_key=True, autoincrement=True)

    # Proper FK (NOT primary key)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    role = Column(String(50), nullable=False, index=True)

    school_id = Column(String(20))
    branch_id = Column(String(20))

    title = Column(String(150))
    message = Column(String(500), nullable=False)
    data = Column(JSON)

    module = Column(String(50), nullable=False, index=True)
    reference_id = Column(String(30))

    priority = Column(String(20), default="NORMAL")
    notification_type = Column(String(30), default="INFO")

    in_app_sent = Column(Boolean, default=True)
    email_sent = Column(Boolean, default=False)
    email_error = Column(String(255))
    sms_sent = Column(Boolean, default=False)
    push_sent = Column(Boolean, default=False)

    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    scheduled_at = Column(DateTime)
    expires_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    #  Relationship must match FK target
    user = relationship("User", back_populates="notifications")


