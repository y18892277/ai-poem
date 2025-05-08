# backend/app/models/battle.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Battle(Base):
    __tablename__ = "battles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    score = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active, win, lose
    current_poetry_id = Column(Integer, ForeignKey("poetry.id"), nullable=True)
    
    # 新增对战详细信息字段
    rounds = Column(Integer, default=0)  # 对战回合数
    current_round = Column(Integer, default=1)  # 当前回合数
    battle_records = Column(JSON, default=dict)  # 对战详细记录，包含每回合的诗词、得分等
    total_time = Column(Integer, default=0)  # 总对战时间（秒）
    avg_response_time = Column(Float, default=0.0)  # 平均响应时间（秒）
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="battles")
    season = relationship("Season", back_populates="battles")
    current_poetry = relationship("Poetry")

    def __repr__(self):
        return f"<Battle {self.id}>"