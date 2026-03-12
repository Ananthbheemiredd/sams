# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import relationship
# from app.database.base import Base
#
# class Role(Base):
#     __tablename__ = "roles"
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(50), unique=True, nullable=False)
#
#     # one role → many users
#     users = relationship("User", back_populates="role")
