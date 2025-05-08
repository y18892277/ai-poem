from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from . import schemas, auth, models, crud
from .models import Base, User, Battle, Season, Poetry
from .core.database import engine, get_db
import logging
import random
from .core.init_db import init_poetry_data



# 创建数据库表
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 在创建数据库表后初始化数据
Base.metadata.create_all(bind=engine)
init_poetry_data(next(get_db()))

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
    try:
        logger.info(f"Attempting to register user: {user.username}")
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            logger.warning(f"Username already exists: {user.username}")
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        hashed_password = auth.get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            nickname=user.nickname or user.username,
            is_active=True,  # 设置默认值
            avatar=None  # 设置默认值
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
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 创建新的对战记录
        battle = models.Battle(
            user_id=current_user.id,
            status="active",
            score=0,
            current_poetry_id=None
        )
        db.add(battle)
        db.commit()
        db.refresh(battle)
        
        # 获取随机诗词作为起始句
        poetry = get_random_poetry(db)
        battle.current_poetry_id = poetry.id
        db.commit()
        
        return battle
    except Exception as e:
        logger.error(f"Error creating battle: {str(e)}")
        raise HTTPException(status_code=500, detail="创建对战失败")
    

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
        poetry1 = db.query(models.Poetry).filter(
            models.Poetry.content == chain_data.poetry1
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
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        battle = db.query(models.Battle).filter(
            models.Battle.id == battle_id,
            models.Battle.user_id == current_user.id
        ).first()
        
        if not battle:
            raise HTTPException(status_code=404, detail="对战记录不存在")
        
        # 更新对战信息
        for field, value in battle_update.dict(exclude_unset=True).items():
            setattr(battle, field, value)
        
        db.commit()
        db.refresh(battle)
        return battle
    except Exception as e:
        logger.error(f"Error updating battle: {str(e)}")
        raise HTTPException(status_code=500, detail="更新对战失败")
    

# 辅助函数
def get_random_poetry(db: Session, difficulty: int = 1) -> models.Poetry:
    """获取随机诗词"""
    poetry = db.query(models.Poetry).order_by(
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