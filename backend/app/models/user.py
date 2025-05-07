from sqlalchemy import Column, String, Integer, Float
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    nickname = Column(String(50))
    total_score = Column(Integer, default=0)
    win_count = Column(Integer, default=0)
    lose_count = Column(Integer, default=0)
    draw_count = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<User {self.username}>" 