from typing import Optional
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        nickname=user.nickname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def update_user_stats(db: Session, user_id: int, is_win: bool, score: int) -> Optional[User]:
    user = get_user(db, user_id)
    if not user:
        return None
    
    user.total_score += score
    if is_win:
        user.win_count += 1
    else:
        user.lose_count += 1
    
    total_games = user.win_count + user.lose_count + user.draw_count
    if total_games > 0:
        user.win_rate = user.win_count / total_games
    
    db.commit()
    db.refresh(user)
    return user 