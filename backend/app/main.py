from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from datetime import timedelta
from . import schemas, auth
from .models import Base, User
from .core.database import engine, get_db

# 创建数据库表
Base.metadata.create_all(bind=engine)

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
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        nickname=user.nickname or user.username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 用户登录
@app.post("/api/v1/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

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