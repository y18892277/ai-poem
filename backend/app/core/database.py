from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 创建数据库引擎
    engine = create_engine(
        settings.get_database_url,
        pool_pre_ping=True,  # 自动检测断开的连接
        pool_recycle=3600,   # 一小时后回收连接
        echo=True  # 打印 SQL 语句，方便调试
    )
    logger.info(f"Successfully created database engine with URL: {settings.get_database_url}")
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