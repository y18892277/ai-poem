from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    nickname: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None

class User(UserBase):
    id: int
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 