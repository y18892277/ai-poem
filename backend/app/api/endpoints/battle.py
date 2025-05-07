from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...schemas.poetry import Poetry, Battle, Season
from ...services import poetry as poetry_service
from ...services import user as user_service
from ...core.security import get_current_user

router = APIRouter()

@router.get("/random-poetry", response_model=Poetry)
def get_random_poetry(
    difficulty: int = 1,
    db: Session = Depends(get_db),
) -> Any:
    """
    获取随机诗词作为起始句
    """
    poetry = poetry_service.get_random_poetry(db, difficulty)
    if not poetry:
        raise HTTPException(status_code=404, detail="No poetry found")
    return poetry

@router.post("/check-chain", response_model=dict)
def check_poetry_chain(
    poetry1: str,
    poetry2: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    检查两句诗是否能够接龙
    """
    can_chain, chain_type = poetry_service.check_poetry_chain(poetry1, poetry2)
    return {
        "can_chain": can_chain,
        "chain_type": chain_type
    }

@router.post("/battle", response_model=Battle)
def create_battle(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """
    创建新的对战
    """
    season = poetry_service.get_active_season(db)
    if not season:
        raise HTTPException(status_code=404, detail="No active season found")
    
    battle = poetry_service.create_battle(
        db,
        BattleCreate(
            user_id=current_user.id,
            season_id=season.id
        )
    )
    return battle

@router.put("/battle/{battle_id}", response_model=Battle)
def update_battle(
    *,
    db: Session = Depends(get_db),
    battle_id: int,
    score: int,
    status: str,
    current_user = Depends(get_current_user),
) -> Any:
    """
    更新对战结果
    """
    battle = poetry_service.update_battle(db, battle_id, score, status)
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    # 更新用户统计信息
    is_win = status == "win"
    user_service.update_user_stats(db, current_user.id, is_win, score)
    
    return battle

@router.get("/season/rankings", response_model=List[dict])
def get_season_rankings(
    *,
    db: Session = Depends(get_db),
    season_id: int,
    limit: int = 10,
) -> Any:
    """
    获取赛季排行榜
    """
    rankings = poetry_service.get_season_rankings(db, season_id, limit)
    result = []
    for user_id, total_score in rankings:
        user = user_service.get_user(db, user_id)
        if user:
            result.append({
                "user_id": user_id,
                "username": user.username,
                "nickname": user.nickname,
                "total_score": total_score
            })
    return result 