from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc
from datetime import timedelta
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from typing import List, Optional, Tuple, Dict, Any
import logging
import re # For parsing poem lines

from .core.database import engine, get_db, Base
from .core.init_database import init_database
from . import schemas, auth
from .models import User, Battle, Season, Poetry, UserFavoritePoetry
from .core.init_db import init_poetry_data, init_season_data
import random
from .schemas.battle import BattleCreate, BattleResponse, ChainSubmitRequest, ChainSubmitResponse
from .crud.battle import get_active_battle, get_battle

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 初始化数据库
    init_database()
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # 初始化数据
    db = next(get_db())
    init_poetry_data(db)
    init_season_data(db)
    logger.info("Initial data loaded successfully")
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    raise

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

@app.post("/api/v1/battles/start", response_model=BattleResponse, tags=["Battle Modes"])
async def start_battle_endpoint(
    battle_create: BattleCreate,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    active_battle = get_active_battle(db, user_id=current_user.id)
    if active_battle:
        # Option 1: Abort existing battle and start a new one (Now active)
        active_battle.status = "aborted"
        db.add(active_battle) # Ensure SQLAlchemy tracks the change
        db.commit() # Commit the change for the aborted battle
        # It might be good to refresh active_battle here if its state is used later before reassigning, but we are creating a new one.
        logger.info(f"User {current_user.id} aborted battle {active_battle.id} to start a new one.")
        # Option 2: Raise error (Now commented out)
        # raise HTTPException(status_code=400, detail=f"User already has an active battle (ID: {active_battle.id}). Finish or abort it first.")

    active_season = db.query(Season).filter(Season.status == "active").order_by(Season.id.desc()).first()
    if not active_season:
        # Fallback: if no active season, use the most recent season
        active_season = db.query(Season).order_by(Season.id.desc()).first()
        if not active_season:
            raise HTTPException(status_code=404, detail="No season found to start a battle.")

    new_battle_data = {
        "user_id": current_user.id,
        "season_id": active_season.id,
        "battle_type": battle_create.battle_type,
        "status": "active",
        "score": 0,
        "rounds": 0,
        "current_round_num": 1,
        "battle_records": [] # Initialize as empty list
    }

    if battle_create.battle_type == "normal_chain":
        random_poetry = db.query(Poetry).order_by(func.random()).first() # func needs to be imported from sqlalchemy
        if not random_poetry or not random_poetry.content:
            raise HTTPException(status_code=500, detail="Could not fetch a poem for normal chain mode.")
        
        lines = parse_poem_lines(random_poetry.content)
        if len(lines) < 2: # Need at least two lines for a question and an answer
            # Try to find another poem if the first one is too short
            for _ in range(5): # Try a few times
                random_poetry = db.query(Poetry).order_by(func.random()).first()
                if random_poetry and random_poetry.content:
                    lines = parse_poem_lines(random_poetry.content)
                    if len(lines) >= 2:
                        break
            if len(lines) < 2:
                 raise HTTPException(status_code=500, detail="Selected poem does not have enough lines for normal chain mode after multiple tries.")

        new_battle_data["current_poetry_id"] = random_poetry.id
        new_battle_data["current_question"] = lines[0] # First line as question
        new_battle_data["expected_answer"] = lines[1]  # Second line as expected answer
        # Record initial state for the first round
        new_battle_data["battle_records"].append(
            schemas.RoundRecord(
                round_num=1, 
                question=lines[0]
            ).model_dump() # Use .model_dump() for Pydantic v2
        )

    elif battle_create.battle_type == "smart_chain":
        ai_line = await get_ai_starting_line(db=db)
        if not ai_line:
            raise HTTPException(status_code=500, detail="AI failed to provide a starting line.")
        new_battle_data["current_question"] = ai_line
        # Record initial state for the first round
        new_battle_data["battle_records"].append(
            schemas.RoundRecord(
                round_num=1, 
                question=ai_line
            ).model_dump()
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid battle_type specified.")

    battle = Battle(**new_battle_data)
    db.add(battle)
    db.commit()
    db.refresh(battle)
    logger.info(f"Battle {battle.id} started for user {current_user.id}, type: {battle.battle_type}")
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

@app.put("/api/v1/battles/{battle_id}", response_model=schemas.BattleResponse)
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
    update_data = battle_update.model_dump(exclude_unset=True) # Pydantic V2
    for key, value in update_data.items():
        setattr(battle, key, value)
    
    db.add(battle) # Add to session before commit if changed
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

@app.get("/api/v1/poetry/{poetry_id}", response_model=schemas.PoetryResponse)
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

# Placeholder AI functions (as discussed)
async def get_ai_starting_line(db: Session = Depends(get_db)) -> str:
    # Implementation of get_ai_starting_line function
    pass

def clean_poem_line(line: str) -> str:
    """Removes common punctuation and leading/trailing spaces from a poem line."""
    if not line: 
        return ""
    # 移除常见标点符号： 中文的 ，。！？； 和英文的 ,.!?; 以及空格
    cleaned_line = re.sub(r"[，。！？；,.!?;\s]+", "", line)
    return cleaned_line.strip()

@app.post("/api/v1/battles/{battle_id}/submit", response_model=ChainSubmitResponse, tags=["Battle Modes"])
async def submit_battle_answer(
    battle_id: int,
    submission: ChainSubmitRequest,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    battle = get_battle(db, battle_id=battle_id) # from crud.battle
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found.")
    if battle.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to submit to this battle.")
    if battle.status != "active":
        raise HTTPException(status_code=400, detail=f"Battle is not active (current status: {battle.status}).")

    user_answer_raw = submission.answer
    user_answer_cleaned = clean_poem_line(user_answer_raw)
    is_correct_answer = False
    message = ""
    next_q_for_normal = None
    ai_next_line_for_smart = None
    points_this_round = 0
    
    # Find the existing round record for the current round to update it with user's answer
    # This assumes the record was created when the question was presented in the start_battle or previous submit.
    # If battle_records is empty or last record is not for current_round_num, it means something is off
    # or it's the very first question of a multi-question-per-round system (not our case here)
    current_round_record_dict = None
    if battle.battle_records and isinstance(battle.battle_records, list):
        # Find the record for the current round to update it
        # If a round record for current_round_num was already added when question was set,
        # we update it. Otherwise, we create a new one.
        # For simplicity, let's assume a round_record is made per submit cycle.
        pass # Will create a new full record below

    # Initialize data for the current round record
    round_data_for_append = {
        "round_num": battle.current_round_num,
        "question": battle.current_question,
        "user_answer": user_answer_raw,
        "is_correct": False, # Default to False
        "ai_judgement": None,
        "points_awarded": 0
    }

    if battle.battle_type == "normal_chain":
        if not battle.expected_answer:
            # This case should ideally not happen if a question is active
            logger.error(f"Normal chain battle {battle.id} has no expected_answer for question '{battle.current_question}'")
            raise HTTPException(status_code=500, detail="Error in battle state: no expected answer.")
        
        expected_answer_cleaned = clean_poem_line(battle.expected_answer)
        
        if user_answer_cleaned == expected_answer_cleaned:
            is_correct_answer = True
            message = "回答正确！"
            points_this_round = 10 # Example points
            battle.score += points_this_round
            
            current_poem = db.query(Poetry).filter(Poetry.id == battle.current_poetry_id).first()
            if not current_poem:
                message += " 但未能加载诗词信息。游戏结束。"
                battle.status = "completed_win" # Or an error status
            else:
                lines = parse_poem_lines(current_poem.content)
                try:
                    # Find index of the just-answered `battle.expected_answer`
                    idx_of_last_correct_answer = lines.index(battle.expected_answer)
                    
                    if idx_of_last_correct_answer + 1 < len(lines):
                        # Next line becomes the new question
                        next_q_for_normal = lines[idx_of_last_correct_answer + 1]
                        if idx_of_last_correct_answer + 2 < len(lines):
                            # And the line after that is the new expected answer
                            battle.expected_answer = lines[idx_of_last_correct_answer + 2]
                        else:
                            # Only one line left, it is the question, no more expected answer for *next* round
                            battle.expected_answer = None # This means after user answers next_q_for_normal, poem ends
                    else:
                        # Poem completed with this correct answer
                        message += " 恭喜！你已完成这首诗的接龙！"
                        battle.status = "completed_win"
                        next_q_for_normal = None # No next question
                        battle.expected_answer = None
                except ValueError:
                    message += " 但在寻找下一句时出现内部错误。游戏结束。"
                    battle.status = "completed_win" # Or an error status
        else:
            is_correct_answer = False
            message = f"回答错误。正确答案应为：{battle.expected_answer}"
            points_this_round = -5 # Example penalty
            battle.score = max(0, battle.score + points_this_round)
            battle.status = "completed_lose"

    elif battle.battle_type == "smart_chain":
        ai_is_correct, ai_message = await check_ai_poetry_chain(battle.current_question, user_answer_raw, db=db)
        is_correct_answer = ai_is_correct
        message = ai_message
        round_data_for_append["ai_judgement"] = ai_message

        if is_correct_answer:
            points_this_round = 15
            battle.score += points_this_round
            ai_next_line_for_smart = await get_ai_response_to_line(user_answer_raw, db=db)
            if not ai_next_line_for_smart:
                message += " AI已词穷，恭喜你获胜！"
                battle.status = "completed_win"
        else:
            points_this_round = -7
            battle.score = max(0, battle.score + points_this_round)
            battle.status = "completed_lose"
    
    round_data_for_append["is_correct"] = is_correct_answer
    round_data_for_append["points_awarded"] = points_this_round
    
    battle.rounds += 1
    # Ensure battle_records is a list before appending
    if not isinstance(battle.battle_records, list):
        battle.battle_records = []
    battle.battle_records.append(round_data_for_append)

    if battle.status == "active":
        battle.current_round_num += 1
        if battle.battle_type == "normal_chain":
            battle.current_question = next_q_for_normal 
            # If next_q_for_normal is None, it means game ended (win/loss handled above)
            if not battle.current_question: # Game ended
                 if battle.status == "active": # Should have been set to win/loss already
                    message = message.replace("回答正确！","") + "诗词已尽，挑战成功！"
                    battle.status = "completed_win"
        elif battle.battle_type == "smart_chain":
            if ai_next_line_for_smart:
                battle.current_question = ai_next_line_for_smart
            elif is_correct_answer: # AI was correct but AI has no next line
                if battle.status == "active": battle.status = "completed_win"
            # If AI was incorrect, status is already completed_lose
    else: # Game has ended (completed_win or completed_lose)
        logger.info(f"Battle {battle.id} ended. Status: {battle.status}, Score: {battle.score}")

    db.add(battle) # Use add for SQLAlchemy to track changes before commit
    db.commit()
    db.refresh(battle)

    final_round_record_obj = schemas.RoundRecord(**round_data_for_append)

    return ChainSubmitResponse(
        is_correct=is_correct_answer,
        message=message,
        next_question=battle.current_question if battle.status == "active" else None, 
        ai_next_line=battle.current_question if battle.status == "active" and battle.battle_type == "smart_chain" else None, 
        updated_battle_state=BattleResponse.model_validate(battle),
        current_round_record=final_round_record_obj
    )

# Helper function to parse poem content into lines
def parse_poem_lines(content: str) -> List[str]:
    if not content:
        return []
    # Splits by common Chinese and English delimiters, keeps non-empty lines
    lines = re.split(r'[，。！？；,.!?;\n\r]+', content) 
    return [line.strip() for line in lines if line.strip()]