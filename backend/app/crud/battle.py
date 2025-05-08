from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from .. import models, schemas

def get_battle(db: Session, battle_id: int) -> Optional[models.Battle]:
    return db.query(models.Battle).filter(models.Battle.id == battle_id).first()

def get_user_battles(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Battle]:
    return db.query(models.Battle).filter(
        models.Battle.user_id == user_id
    ).offset(skip).limit(limit).all()

def create_battle(db: Session, user_id: int, season_id: Optional[int] = None) -> models.Battle:
    db_battle = models.Battle(
        user_id=user_id,
        season_id=season_id,
        score=0,
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_battle)
    db.commit()
    db.refresh(db_battle)
    return db_battle

def update_battle(db: Session, battle_id: int, battle: schemas.BattleUpdate) -> Optional[models.Battle]:
    db_battle = get_battle(db, battle_id)
    if not db_battle:
        return None
    
    update_data = battle.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_battle, field, value)
    
    db_battle.updated_at = datetime.now()
    db.commit()
    db.refresh(db_battle)
    return db_battle

def delete_battle(db: Session, battle_id: int) -> bool:
    db_battle = get_battle(db, battle_id)
    if not db_battle:
        return False
    
    db.delete(db_battle)
    db.commit()
    return True

def get_active_battle(db: Session, user_id: int) -> Optional[models.Battle]:
    return db.query(models.Battle).filter(
        models.Battle.user_id == user_id,
        models.Battle.status == "active"
    ).first() 