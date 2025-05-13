from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class RoundRecord(Base):
    __tablename__ = "round_records"

    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(Integer, ForeignKey("battles.id"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    user_input = Column(Text)
    ai_response = Column(Text, nullable=True) # AI 的回应，可能是下一句诗，也可能没有
    expected_answer = Column(Text, nullable=True) # 常规模式下的预期答案
    is_correct = Column(Boolean, nullable=True) # 用户回答是否正确 (智能模式下可能只判断规则)
    score_change = Column(Integer, default=0)
    message = Column(String(500), nullable=True) # 记录回合结果的消息
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    battle = relationship("Battle", back_populates="round_records") 