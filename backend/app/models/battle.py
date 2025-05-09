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
    status = Column(String(20), default="pending")  # pending, active, completed_win, completed_lose, aborted
    battle_type = Column(String(50), nullable=False) # e.g., "normal_chain", "smart_chain"
    
    current_question = Column(String(500), nullable=True)
    expected_answer = Column(String(500), nullable=True)  # For normal_chain mode
    current_poetry_id = Column(Integer, ForeignKey("poetry.id"), nullable=True)
    
    rounds = Column(Integer, default=0)  # Total rounds played in this battle
    current_round_num = Column(Integer, default=1) # Renamed from current_round
    battle_records = Column(JSON, default=list) # Default to list for easier appending
    
    total_time = Column(Integer, default=0) 
    avg_response_time = Column(Float, default=0.0) 
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="battles")
    season = relationship("Season", back_populates="battles")
    current_poetry_obj = relationship("Poetry", foreign_keys=[current_poetry_id])

    def __repr__(self):
        return f"<Battle id={self.id} type='{self.battle_type}' status='{self.status}' user_id={self.user_id}>"