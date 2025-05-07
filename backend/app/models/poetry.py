from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Poetry(BaseModel):
    __tablename__ = "poetries"
    
    content = Column(String(500), nullable=False)
    author = Column(String(50))
    dynasty = Column(String(50))
    title = Column(String(100))
    difficulty = Column(Integer, default=1)  # 1-5级难度
    
    def __repr__(self):
        return f"<Poetry {self.title}>"

class Battle(BaseModel):
    __tablename__ = "battles"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    season_id = Column(Integer, ForeignKey("seasons.id"))
    score = Column(Integer, default=0)
    status = Column(String(20))  # win, lose, draw
    
    user = relationship("User", back_populates="battles")
    season = relationship("Season", back_populates="battles")
    
    def __repr__(self):
        return f"<Battle {self.id}>"

class Season(BaseModel):
    __tablename__ = "seasons"
    
    name = Column(String(100), nullable=False)
    start_date = Column(String(20))
    end_date = Column(String(20))
    status = Column(String(20))  # active, ended
    
    battles = relationship("Battle", back_populates="season")
    
    def __repr__(self):
        return f"<Season {self.name}>" 