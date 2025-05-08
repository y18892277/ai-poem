from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List
from .. import models, schemas

def get_poetry(db: Session, poetry_id: int) -> Optional[models.Poetry]:
    return db.query(models.Poetry).filter(models.Poetry.id == poetry_id).first()

def get_random_poetry(db: Session, difficulty: int = 1) -> Optional[models.Poetry]:
    return db.query(models.Poetry).filter(
        models.Poetry.difficulty <= difficulty
    ).order_by(func.random()).first()

def create_poetry(db: Session, poetry: schemas.PoetryCreate) -> models.Poetry:
    db_poetry = models.Poetry(
        **poetry.dict(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_poetry)
    db.commit()
    db.refresh(db_poetry)
    return db_poetry

def update_poetry(db: Session, poetry_id: int, poetry: schemas.PoetryUpdate) -> Optional[models.Poetry]:
    db_poetry = get_poetry(db, poetry_id)
    if not db_poetry:
        return None
    
    update_data = poetry.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_poetry, field, value)
    
    db_poetry.updated_at = datetime.now()
    db.commit()
    db.refresh(db_poetry)
    return db_poetry

def delete_poetry(db: Session, poetry_id: int) -> bool:
    db_poetry = get_poetry(db, poetry_id)
    if not db_poetry:
        return False
    
    db.delete(db_poetry)
    db.commit()
    return True

def get_poetry_by_content(db: Session, content: str) -> Optional[models.Poetry]:
    return db.query(models.Poetry).filter(models.Poetry.content.contains(content)).first()

def check_poetry_chain(poetry1: str, poetry2: str) -> tuple[bool, str]:
    """检查诗词接龙是否有效"""
    # 去除标点符号和空格
    p1 = ''.join(c for c in poetry1 if c.isalnum())
    p2 = ''.join(c for c in poetry2 if c.isalnum())
    
    # 检查首尾字接龙
    if p1[-1] == p2[0]:
        return True, "首尾字接龙"
    
    return False, "无效接龙" 