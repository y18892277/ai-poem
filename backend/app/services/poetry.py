from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from ..models.poetry import Poetry, Battle, Season
from ..schemas.poetry import PoetryCreate, BattleCreate, SeasonCreate
import random

def get_poetry(db: Session, poetry_id: int) -> Optional[Poetry]:
    return db.query(Poetry).filter(Poetry.id == poetry_id).first()

def get_random_poetry(db: Session, difficulty: int = 1) -> Optional[Poetry]:
    return db.query(Poetry).filter(Poetry.difficulty == difficulty).order_by(db.func.random()).first()

def create_poetry(db: Session, poetry: PoetryCreate) -> Poetry:
    db_poetry = Poetry(**poetry.dict())
    db.add(db_poetry)
    db.commit()
    db.refresh(db_poetry)
    return db_poetry

def check_poetry_chain(poetry1: str, poetry2: str) -> Tuple[bool, str]:
    """
    检查两句诗是否能够接龙
    返回: (是否可接龙, 接龙类型)
    """
    # 首尾字接龙
    if poetry1[-1] == poetry2[0]:
        return True, "首尾字接龙"
    
    # 韵脚接龙（简单实现，实际应该使用更复杂的韵脚判断）
    if poetry1[-1] == poetry2[-1]:
        return True, "韵脚接龙"
    
    return False, "无法接龙"

def create_battle(db: Session, battle: BattleCreate) -> Battle:
    db_battle = Battle(**battle.dict())
    db.add(db_battle)
    db.commit()
    db.refresh(db_battle)
    return db_battle

def update_battle(db: Session, battle_id: int, score: int, status: str) -> Optional[Battle]:
    battle = db.query(Battle).filter(Battle.id == battle_id).first()
    if not battle:
        return None
    
    battle.score = score
    battle.status = status
    db.commit()
    db.refresh(battle)
    return battle

def get_active_season(db: Session) -> Optional[Season]:
    return db.query(Season).filter(Season.status == "active").first()

def create_season(db: Session, season: SeasonCreate) -> Season:
    db_season = Season(**season.dict())
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season

def get_season_rankings(db: Session, season_id: int, limit: int = 10) -> List[Tuple[int, int]]:
    """
    获取赛季排行榜
    返回: [(用户ID, 总分)]
    """
    return db.query(Battle.user_id, db.func.sum(Battle.score).label('total_score'))\
        .filter(Battle.season_id == season_id)\
        .group_by(Battle.user_id)\
        .order_by(db.desc('total_score'))\
        .limit(limit)\
        .all() 