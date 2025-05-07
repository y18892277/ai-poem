from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 创建数据库引擎
    database_url = settings.get_database_url
    logger.info(f"Using database URL: {database_url}")

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=True
    )
    logger.info("Successfully created database engine")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()