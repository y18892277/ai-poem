from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional

class SeasonBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    start_time: datetime
    end_time: datetime

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v

class SeasonCreate(SeasonBase):
    pass

class SeasonResponse(SeasonBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

class RankingBase(BaseModel):
    score: int = 0
    total_battles: int = 0
    win_count: int = 0
    lose_count: int = 0
    win_rate: float = 0.0

class RankingCreate(RankingBase):
    user_id: int
    season_id: int

class UserInfo(BaseModel):
    id: int
    username: str
    nickname: Optional[str]
    avatar: Optional[str]

    class Config:
        orm_mode = True

class SeasonInfo(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        orm_mode = True

class RankingResponse(RankingBase):
    id: int
    user_id: int
    season_id: int
    created_at: datetime
    updated_at: datetime
    user: UserInfo
    season: SeasonInfo

    class Config:
        orm_mode = True

class RankingsResponse(BaseModel):
    rankings: List[RankingResponse]
    total: int 