from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class Season(Base):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    rankings = relationship('Ranking', back_populates='season')

    @property
    def is_active(self):
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time

class Ranking(Base):
    __tablename__ = 'rankings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    score = Column(Integer, default=0)
    total_battles = Column(Integer, default=0)
    win_count = Column(Integer, default=0)
    lose_count = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    user = relationship('User', back_populates='rankings')
    season = relationship('Season', back_populates='rankings')

    def update_stats(self, is_win: bool):
        """
        更新用户战绩统计
        """
        self.total_battles += 1
        if is_win:
            self.win_count += 1
            self.score += 10  # 胜利加10分
        else:
            self.lose_count += 1
            self.score = max(0, self.score - 5)  # 失败扣5分，但不低于0分
        
        self.win_rate = (self.win_count / self.total_battles) * 100 if self.total_battles > 0 else 0.0 