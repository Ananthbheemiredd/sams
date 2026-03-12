from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, func, Integer
from sqlalchemy.orm import relationship
from app.database.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    # SINGLE PRIMARY KEY
    session_id = Column(String(64), primary_key=True, index=True)

    # Normal FK (NOT primary key)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    role_type = Column(String(50), nullable=False)
    jwt_token = Column(Text)

    device_type = Column(String(30))
    device_name = Column(String(100))
    ip_address = Column(String(50))

    login_time = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
    logout_time = Column(DateTime)

    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sessions")
