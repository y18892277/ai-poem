from pydantic import BaseModel, EmailStr
from typing import Optional, List
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

class Season(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SeasonCreate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    status: str = "active"

class Poetry(BaseModel):
    id: int
    title: str
    author: str
    dynasty: str
    content: str
    type: str
    tags: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PoetryBase(BaseModel):
    title: str
    author: str
    dynasty: str
    content: str
    type: str
    tags: Optional[str] = None

class PoetryCreate(PoetryBase):
    pass

class PoetryUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    dynasty: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[str] = None

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

class PoetryFavoriteResponse(BaseModel):
    success: bool
    message: str

    class Config:
        from_attributes = True 