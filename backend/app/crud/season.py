from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from .. import models, schemas

def get_season(db: Session, season_id: int) -> Optional[models.Season]:
    return db.query(models.Season).filter(models.Season.id == season_id).first()

def get_active_season(db: Session) -> Optional[models.Season]:
    return db.query(models.Season).filter(models.Season.status == "active").first()

def get_seasons(db: Session, skip: int = 0, limit: int = 100) -> List[models.Season]:
    return db.query(models.Season).offset(skip).limit(limit).all()

def create_season(db: Session, season: schemas.SeasonCreate) -> models.Season:
    db_season = models.Season(
        **season.dict(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season

def update_season(db: Session, season_id: int, season: schemas.SeasonUpdate) -> Optional[models.Season]:
    db_season = get_season(db, season_id)
    if not db_season:
        return None
    
    update_data = season.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_season, field, value)
    
    db_season.updated_at = datetime.now()
    db.commit()
    db.refresh(db_season)
    return db_season

def delete_season(db: Session, season_id: int) -> bool:
    db_season = get_season(db, season_id)
    if not db_season:
        return False
    
    db.delete(db_season)
    db.commit()
    return True 