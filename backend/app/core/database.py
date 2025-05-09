from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from .config import settings
from ..models.base import Base

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 构建数据库URL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"

# 创建数据库引擎
try:
    logger.info(f"Using database URL: {SQLALCHEMY_DATABASE_URL}")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        max_overflow=5,
        pool_size=5,
        echo=True
    )
    logger.info("Successfully created database engine")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()