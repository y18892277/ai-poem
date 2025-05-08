from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc
from datetime import timedelta
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from typing import List, Optional
import logging

from .core.database import engine, get_db
from . import schemas, auth
from .models import Base, User, Battle, Season, Poetry, UserFavoritePoetry
from .core.init_db import init_poetry_data, init_season_data
import random

# 删除并重新创建数据库表（仅在开发环境使用）
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 在创建数据库表后初始化数据
init_poetry_data(next(get_db()))
init_season_data(next(get_db()))

app = FastAPI(
    title="诗词接龙游戏API",
    description="诗词接龙游戏的后端API服务",
    version="1.0.0",
    docs_url=None,  # 禁用默认的 docs
    redoc_url=None  # 禁用默认的 redoc
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义 OpenAPI 文档
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="诗词接龙游戏API",
        version="1.0.0",
        description="诗词接龙游戏的后端API服务",
        routes=app.routes,
    )
    
    # 添加安全模式
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 自定义文档路由
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="诗词接龙游戏API - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="诗词接龙游戏API - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return app.openapi()

# 根路由
@app.get("/")
async def root():
    return {
        "message": "欢迎使用诗词接龙游戏API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


# API 健康检查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# 用户注册
@app.post("/api/v1/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to register user: {user.username}")
        
        # 检查用户名是否已存在
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            logger.warning(f"Username already exists: {user.username}")
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已注册
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 创建新用户
        hashed_password = auth.get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            nickname=user.nickname or user.username,
            is_active=True,
            avatar=None
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Successfully registered user: {user.username}")
        return db_user
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        raise

# 用户登录
@app.post("/api/v1/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting login for user: {form_data.username}")
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user:
            logger.warning(f"Login failed: User not found - {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not auth.verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Login failed: Invalid password for user - {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        logger.info(f"Login successful for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise

# 获取当前用户信息
@app.get("/api/v1/users/me", response_model=schemas.User)
async def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return current_user

# 更新用户信息
@app.put("/api/v1/users/me", response_model=schemas.User)
async def update_user(
    user_update: schemas.UserUpdate,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.nickname:
        current_user.nickname = user_update.nickname
    if user_update.email:
        current_user.email = user_update.email
    if user_update.avatar:
        current_user.avatar = user_update.avatar
    
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/api/v1/battle/create", response_model=schemas.Battle)
async def create_battle(
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # 获取当前赛季
    current_season = db.query(Season).filter(Season.status == "active").first()
    if not current_season:
        raise HTTPException(status_code=404, detail="没有进行中的赛季")
    
    # 创建新对战
    battle = Battle(
        user_id=current_user.id,
        season_id=current_season.id,
        status="active"
    )
    
    db.add(battle)
    db.commit()
    db.refresh(battle)
    return battle

@app.get("/api/v1/battle/random-poetry", response_model=schemas.Poetry)
async def get_random_poetry_endpoint(
    difficulty: int = 1,
    db: Session = Depends(get_db)
):
    try:
        poetry = get_random_poetry(db, difficulty)
        return poetry
    except Exception as e:
        logger.error(f"Error getting random poetry: {str(e)}")
        raise HTTPException(status_code=500, detail="获取随机诗词失败")

@app.post("/api/v1/battle/check-chain")
async def check_poetry_chain(
    chain_data: schemas.PoetryChain,
    db: Session = Depends(get_db)
):
    try:
        # 获取前一句诗词
        poetry1 = db.query(Poetry).filter(
            Poetry.content == chain_data.poetry1
        ).first()
        
        if not poetry1:
            raise HTTPException(status_code=400, detail="前一句诗词不存在")
        
        # 检查接龙是否有效
        can_chain, chain_type = check_poetry_chain_valid(
            poetry1.content,
            chain_data.poetry2
        )
        
        return {
            "can_chain": can_chain,
            "chain_type": chain_type
        }
    except Exception as e:
        logger.error(f"Error checking poetry chain: {str(e)}")
        raise HTTPException(status_code=500, detail="检查接龙失败")

@app.put("/api/v1/battle/{battle_id}", response_model=schemas.Battle)
async def update_battle(
    battle_id: int,
    battle_update: schemas.BattleUpdate,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # 获取对战记录
    battle = db.query(Battle).filter(Battle.id == battle_id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="对战记录不存在")
    
    # 检查权限
    if battle.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限修改此对战记录")
    
    # 更新对战记录
    for key, value in battle_update.dict(exclude_unset=True).items():
        setattr(battle, key, value)
    
    db.commit()
    db.refresh(battle)
    return battle

# 辅助函数
def get_random_poetry(db: Session, difficulty: int = 1) -> Poetry:
    """获取随机诗词"""
    poetry = db.query(Poetry).order_by(
        func.random()
    ).first()
    
    if not poetry:
        raise HTTPException(status_code=404, detail="没有可用的诗词")
    
    return poetry

def check_poetry_chain_valid(poetry1: str, poetry2: str) -> tuple[bool, str]:
    """检查诗词接龙是否有效"""
    # 去除标点符号和空格
    p1 = ''.join(c for c in poetry1 if c.isalnum())
    p2 = ''.join(c for c in poetry2 if c.isalnum())
    
    # 检查首尾字接龙
    if p1[-1] == p2[0]:
        return True, "首尾字接龙"
    
    return False, "无效接龙"

# 获取赛季列表
@app.get("/api/v1/seasons", response_model=List[schemas.Season])
async def get_seasons(db: Session = Depends(get_db)):
    try:
        seasons = db.query(Season).all()
        return seasons
    except Exception as e:
        logger.error(f"Error getting seasons: {str(e)}")
        raise HTTPException(status_code=500, detail="获取赛季列表失败")

# 获取排行榜
@app.get("/api/v1/rankings")
async def get_rankings(
    season: Optional[int] = None,
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    try:
        # 构建基础查询
        query = db.query(
            User.id,
            User.username,
            User.nickname,
            User.avatar,
            func.sum(Battle.score).label('score'),
            func.count(Battle.id).label('totalBattles'),
            func.sum(case([(Battle.status == 'win', 1)], else_=0)).label('winCount'),
            func.sum(case([(Battle.status == 'lose', 1)], else_=0)).label('loseCount')
        ).join(Battle, User.id == Battle.user_id)

        # 如果指定了赛季，添加赛季过滤
        if season:
            query = query.filter(Battle.season_id == season)

        # 分组和排序
        query = query.group_by(User.id)\
                    .order_by(desc('score'))

        # 计算总数
        total = query.count()

        # 分页
        rankings = query.offset((page - 1) * pageSize)\
                       .limit(pageSize)\
                       .all()

        # 格式化结果
        result = []
        for r in rankings:
            result.append({
                "id": r.id,
                "username": r.username,
                "nickname": r.nickname,
                "avatar": r.avatar,
                "score": r.score or 0,
                "totalBattles": r.totalBattles or 0,
                "winCount": r.winCount or 0,
                "loseCount": r.loseCount or 0,
                "winRate": round((r.winCount or 0) / (r.totalBattles or 1) * 100, 2)
            })

        return {
            "success": True,
            "rankings": result,
            "total": total
        }
    except Exception as e:
        logger.error(f"Error getting rankings: {str(e)}")
        raise HTTPException(status_code=500, detail="获取排行榜失败")

# 诗词库相关API
@app.get("/v1/poetry/list", response_model=schemas.PoetryListResponse)
async def get_poetry_list(
    page: int = 1,
    pageSize: int = 10,
    dynasty: Optional[str] = None,
    type: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        # 构建基础查询
        query = db.query(Poetry)

        # 添加过滤条件
        if dynasty:
            query = query.filter(Poetry.dynasty == dynasty)
        if type:
            query = query.filter(Poetry.type == type)
        if keyword:
            query = query.filter(
                Poetry.content.contains(keyword) |
                Poetry.title.contains(keyword) |
                Poetry.author.contains(keyword)
            )

        # 计算总数
        total = query.count()

        # 分页
        poetry_list = query.offset((page - 1) * pageSize)\
                          .limit(pageSize)\
                          .all()

        return {
            "success": True,
            "data": poetry_list,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    except Exception as e:
        logger.error(f"Error getting poetry list: {str(e)}")
        raise HTTPException(status_code=500, detail="获取诗词列表失败")

@app.get("/v1/poetry/{poetry_id}", response_model=schemas.PoetryResponse)
async def get_poetry_detail(
    poetry_id: int,
    db: Session = Depends(get_db)
):
    try:
        poetry = db.query(Poetry).filter(Poetry.id == poetry_id).first()
        if not poetry:
            raise HTTPException(status_code=404, detail="诗词不存在")
        return {
            "success": True,
            "data": poetry
        }
    except Exception as e:
        logger.error(f"Error getting poetry detail: {str(e)}")
        raise HTTPException(status_code=500, detail="获取诗词详情失败")

@app.get("/v1/poetry/favorites", response_model=schemas.PoetryListResponse)
async def get_favorite_poetry(
    current_user: User = Depends(auth.get_current_user),
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    try:
        # 获取用户收藏的诗词
        query = db.query(Poetry)\
                 .join(UserFavoritePoetry)\
                 .filter(UserFavoritePoetry.user_id == current_user.id)

        # 计算总数
        total = query.count()

        # 分页
        favorites = query.offset((page - 1) * pageSize)\
                        .limit(pageSize)\
                        .all()

        return {
            "success": True,
            "data": favorites,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    except Exception as e:
        logger.error(f"Error getting favorite poetry: {str(e)}")
        raise HTTPException(status_code=500, detail="获取收藏列表失败")

@app.post("/v1/poetry/{poetry_id}/favorite", response_model=schemas.PoetryFavoriteResponse)
async def toggle_favorite_poetry(
    poetry_id: int,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 检查诗词是否存在
        poetry = db.query(Poetry).filter(Poetry.id == poetry_id).first()
        if not poetry:
            raise HTTPException(status_code=404, detail="诗词不存在")

        # 检查是否已收藏
        favorite = db.query(UserFavoritePoetry)\
                    .filter(
                        UserFavoritePoetry.user_id == current_user.id,
                        UserFavoritePoetry.poetry_id == poetry_id
                    ).first()

        if favorite:
            # 取消收藏
            db.delete(favorite)
            message = "取消收藏成功"
        else:
            # 添加收藏
            favorite = UserFavoritePoetry(
                user_id=current_user.id,
                poetry_id=poetry_id
            )
            db.add(favorite)
            message = "收藏成功"

        db.commit()
        return {"success": True, "message": message}
    except Exception as e:
        logger.error(f"Error toggling favorite poetry: {str(e)}")
        raise HTTPException(status_code=500, detail="操作收藏失败")