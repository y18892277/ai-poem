from pydantic import BaseModel
from typing import Optional, List

class PoetryBase(BaseModel):
    content: str
    author: Optional[str] = None
    dynasty: Optional[str] = None
    title: Optional[str] = None
    difficulty: Optional[int] = 1

class PoetryCreate(PoetryBase):
    pass

class PoetryUpdate(PoetryBase):
    pass

class PoetryInDBBase(PoetryBase):
    id: int

    class Config:
        orm_mode = True

class Poetry(PoetryInDBBase):
    pass

class BattleBase(BaseModel):
    user_id: int
    season_id: int
    score: int = 0
    status: str = "pending"

class BattleCreate(BattleBase):
    pass

class BattleUpdate(BaseModel):
    score: Optional[int] = None
    status: Optional[str] = None

class BattleInDBBase(BattleBase):
    id: int

    class Config:
        orm_mode = True

class Battle(BattleInDBBase):
    pass

class SeasonBase(BaseModel):
    name: str
    start_date: str
    end_date: str
    status: str = "active"

class SeasonCreate(SeasonBase):
    pass

class SeasonUpdate(BaseModel):
    status: Optional[str] = None

class SeasonInDBBase(SeasonBase):
    id: int

    class Config:
        orm_mode = True

class Season(SeasonInDBBase):
    pass 