from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SeasonBase(BaseModel):
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = "upcoming"  # upcoming, active, completed

class SeasonCreate(SeasonBase):
    pass

class SeasonUpdate(SeasonBase):
    pass

class Season(SeasonBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True