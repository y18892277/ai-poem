from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any

# Battle基础模型
class BattleBase(BaseModel):
    user_id: Optional[int] = None
    season_id: Optional[int] = None
    score: Optional[int] = 0
    status: Optional[str] = "pending"  # pending, active, completed_win, completed_lose, aborted
    battle_type: Optional[str] = None # e.g., "normal_chain", "smart_chain"
    current_question: Optional[str] = None
    expected_answer: Optional[str] = None # For normal_chain mode
    current_poetry_id: Optional[int] = None
    rounds: Optional[int] = 0
    current_round_num: Optional[int] = 1
    battle_records: Optional[List[Any]] = Field(default_factory=list)

# 创建Battle时的请求模型
class BattleCreate(BaseModel):
    battle_type: str = Field(..., examples=["normal_chain", "smart_chain"])

# 更新Battle时的请求模型 (如果需要一个独立的更新模型)
class BattleUpdate(BaseModel):
    score: Optional[int] = None
    status: Optional[str] = None
    current_question: Optional[str] = None
    expected_answer: Optional[str] = None
    rounds: Optional[int] = None
    current_round_num: Optional[int] = None
    battle_records: Optional[List[Any]] = None

# Battle响应模型 (之前这里错误地命名为 Battle)
class BattleResponse(BattleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schemas for submitting answers in chain modes
class ChainSubmitRequest(BaseModel):
    answer: str

class RoundRecord(BaseModel):
    round_num: int
    question: str
    user_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    ai_judgement: Optional[str] = None # For smart_chain mode
    points_awarded: Optional[int] = 0

class ChainSubmitResponse(BaseModel):
    is_correct: bool
    message: str
    next_question: Optional[str] = None
    ai_next_line: Optional[str] = None # For smart_chain, if AI provides the next line
    updated_battle_state: BattleResponse
    current_round_record: Optional[RoundRecord] = None