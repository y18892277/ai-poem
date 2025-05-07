from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    nickname: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    total_score: int
    win_count: int
    lose_count: int
    draw_count: int
    win_rate: float

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None 