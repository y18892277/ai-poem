from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base
# 注意：我们不需要显式导入 UserFavoritePoetry，因为关系使用的是字符串

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    nickname = Column(String(50))
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100))
    avatar = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    rankings = relationship("Ranking", back_populates="user")
    battles = relationship("Battle", back_populates="user")
    favorite_poetry = relationship("UserFavoritePoetry", back_populates="user") 