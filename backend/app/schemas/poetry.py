from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PoetryBase(BaseModel):
    title: str
    author: str
    dynasty: str
    content: str
    type: Optional[str] = None
    tags: Optional[str] = None
    difficulty: Optional[int] = 1

class PoetryCreate(PoetryBase):
    pass

class PoetryUpdate(PoetryBase):
    pass

class Poetry(PoetryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PoetryResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Poetry] = None

    class Config:
        from_attributes = True

class PoetryListResponse(BaseModel):
    success: bool
    data: List[Poetry]
    total: int
    page: int
    pageSize: int

    class Config:
        from_attributes = True


class PoetryChain(BaseModel):
    poetry1: str  # 前一句诗词
    poetry2: str  # 接龙的诗词
    chain_type: Optional[str] = None  # 接龙类型（如：首尾字接龙、意境接龙等）

    class Config:
        from_attributes = True

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