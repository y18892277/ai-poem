from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.rankings import Season, Ranking
from ..models.users import User
from ..schemas.rankings import (
    SeasonCreate,
    SeasonResponse,
    RankingResponse,
    RankingsResponse
)
from ..dependencies import get_current_user

router = APIRouter()  # 移除prefix，在main.py中统一添加

@router.get("/seasons", response_model=List[SeasonResponse])
async def get_seasons(db: Session = Depends(get_db)):
    """获取所有赛季"""
    seasons = db.query(Season).order_by(Season.start_time.desc()).all()
    return [
        {
            "id": season.id,
            "name": season.name,
            "start_time": season.start_time,
            "end_time": season.end_time,
            "created_at": season.created_at,
            "updated_at": season.updated_at,
            "is_active": season.is_active
        }
        for season in seasons
    ]

@router.post("/seasons", response_model=SeasonResponse)
async def create_season(
    season: SeasonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新赛季（仅管理员）"""
    print(f"Received season data: {season}")  # 调试日志
    print(f"Current user: {current_user}")    # 调试日志

    if not current_user or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 检查时间是否合法
    if season.start_time >= season.end_time:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")
    
    # 检查是否与其他赛季时间重叠
    overlapping = db.query(Season).filter(
        Season.start_time <= season.end_time,
        Season.end_time >= season.start_time
    ).first()
    if overlapping:
        raise HTTPException(status_code=400, detail="赛季时间与现有赛季重叠")
    
    try:
        new_season = Season(
            name=season.name,
            start_time=season.start_time,
            end_time=season.end_time
        )
        db.add(new_season)
        db.commit()
        db.refresh(new_season)
        
        return {
            "id": new_season.id,
            "name": new_season.name,
            "start_time": new_season.start_time,
            "end_time": new_season.end_time,
            "created_at": new_season.created_at,
            "updated_at": new_season.updated_at,
            "is_active": new_season.is_active
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating season: {e}")  # 调试日志
        raise HTTPException(status_code=500, detail=f"创建赛季失败: {str(e)}")

@router.get("/rankings", response_model=RankingsResponse)
async def get_rankings(
    season_id: Optional[int] = None,
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=50),
    db: Session = Depends(get_db)
):
    """获取排行榜"""
    # 构建基础查询
    query = db.query(Ranking).join(User)
    
    # 如果指定了赛季，则按赛季筛选
    if season_id:
        season = db.query(Season).filter(Season.id == season_id).first()
        if not season:
            raise HTTPException(status_code=404, detail="赛季不存在")
        query = query.filter(Ranking.season_id == season_id)
    else:
        # 默认使用当前进行中的赛季
        current_season = db.query(Season).filter(
            Season.start_time <= datetime.utcnow(),
            Season.end_time >= datetime.utcnow()
        ).first()
        if current_season:
            query = query.filter(Ranking.season_id == current_season.id)
    
    # 计算总数
    total = query.count()
    
    # 获取分页数据
    rankings = query.order_by(Ranking.score.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    return {
        "rankings": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "season_id": r.season_id,
                "score": r.score,
                "total_battles": r.total_battles,
                "win_count": r.win_count,
                "lose_count": r.lose_count,
                "win_rate": r.win_rate,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "user": {
                    "id": r.user.id,
                    "username": r.user.username,
                    "nickname": r.user.nickname,
                    "avatar": r.user.avatar
                },
                "season": {
                    "id": r.season.id,
                    "name": r.season.name,
                    "is_active": r.season.is_active
                }
            }
            for r in rankings
        ],
        "total": total
    }

@router.get("/rankings/{user_id}", response_model=RankingResponse)
async def get_user_ranking(
    user_id: int,
    season_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取指定用户的排名信息"""
    query = db.query(Ranking).filter(Ranking.user_id == user_id)
    
    if season_id:
        query = query.filter(Ranking.season_id == season_id)
    else:
        current_season = db.query(Season).filter(
            Season.start_time <= datetime.utcnow(),
            Season.end_time >= datetime.utcnow()
        ).first()
        if current_season:
            query = query.filter(Ranking.season_id == current_season.id)
    
    ranking = query.first()
    if not ranking:
        raise HTTPException(status_code=404, detail="未找到该用户的排名信息")
    
    return {
        "id": ranking.id,
        "user_id": ranking.user_id,
        "season_id": ranking.season_id,
        "score": ranking.score,
        "total_battles": ranking.total_battles,
        "win_count": ranking.win_count,
        "lose_count": ranking.lose_count,
        "win_rate": ranking.win_rate,
        "created_at": ranking.created_at,
        "updated_at": ranking.updated_at,
        "user": {
            "id": ranking.user.id,
            "username": ranking.user.username,
            "nickname": ranking.user.nickname,
            "avatar": ranking.user.avatar
        },
        "season": {
            "id": ranking.season.id,
            "name": ranking.season.name,
            "is_active": ranking.season.is_active
        }
    } 