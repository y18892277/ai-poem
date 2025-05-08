# backend/app/models/battle.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..core.database import Base
from datetime import datetime

class Battle(Base):
    __tablename__ = "battles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="active")  # active, completed, abandoned
    score = Column(Integer, default=0)
    current_poetry_id = Column(Integer, ForeignKey("poetry.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="battles")
    current_poetry = relationship("Poetry")