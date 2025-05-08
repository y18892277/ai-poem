from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from .config import settings
from ..models.base import Base

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库引擎
try:
    logger.info(f"Using database URL: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    logger.info("Successfully created database engine")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()