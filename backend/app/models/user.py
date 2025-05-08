from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    # 添加主键
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(200))  # 添加头像字段
    is_active = Column(Boolean, default=True)  # 添加 is_active 字段
    
    # 统计字段
    total_score = Column(Integer, default=0)
    win_count = Column(Integer, default=0)
    lose_count = Column(Integer, default=0)
    draw_count = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # 新增游戏统计字段
    max_win_streak = Column(Integer, default=0)  # 最高连胜次数
    current_win_streak = Column(Integer, default=0)  # 当前连胜次数
    highest_score = Column(Integer, default=0)  # 最高得分
    current_rank = Column(String(20), default="新手")  # 当前段位
    rank_score = Column(Integer, default=0)  # 段位积分
    total_battles = Column(Integer, default=0)  # 总对战次数
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 添加关系
    battles = relationship("Battle", back_populates="user")
    favorite_poetry = relationship("UserFavoritePoetry", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"