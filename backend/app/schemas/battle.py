from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Battle基础模型
class BattleBase(BaseModel):
    user_id: Optional[int] = None
    season_id: Optional[int] = None
    score: Optional[int] = 0
    status: Optional[str] = "pending"  # pending, active, completed
    current_poetry_id: Optional[int] = None

# 创建Battle时的请求模型
class BattleCreate(BattleBase):
    pass

# 更新Battle时的请求模型
class BattleUpdate(BattleBase):
    pass

# Battle响应模型
class Battle(BattleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True