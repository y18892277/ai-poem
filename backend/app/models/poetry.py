from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Poetry(Base):
    __tablename__ = "poetry"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(50), nullable=False)
    dynasty = Column(String(20), nullable=False)
    content = Column(String(1000), nullable=False)
    type = Column(String(20), nullable=False)
    tags = Column(String(200))
    difficulty = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 添加关系
    favorited_by = relationship("UserFavoritePoetry", back_populates="poetry")

    def __repr__(self):
        return f"<Poetry {self.title}>"

class UserFavoritePoetry(Base):
    __tablename__ = "user_favorite_poetry"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    poetry_id = Column(Integer, ForeignKey("poetry.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    user = relationship("User", back_populates="favorite_poetry")
    poetry = relationship("Poetry", back_populates="favorited_by")

    def __repr__(self):
        return f"<UserFavoritePoetry user_id={self.user_id} poetry_id={self.poetry_id}>"
