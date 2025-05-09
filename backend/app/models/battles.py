from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class Battle(Base):
    __tablename__ = "battles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    poetry_id = Column(Integer, ForeignKey("poetry.id"), nullable=False)
    user_answer = Column(String(200), nullable=False)
    is_correct = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="battles")
    season = relationship("Season")
    poetry = relationship("Poetry") 