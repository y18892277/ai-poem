from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    # 添加主键
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(200))  # 添加头像字段
    is_active = Column(Boolean, default=True)  # 添加 is_active 字段
    total_score = Column(Integer, default=0)
    win_count = Column(Integer, default=0)
    lose_count = Column(Integer, default=0)
    draw_count = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # 添加关系
    battles = relationship("Battle", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"