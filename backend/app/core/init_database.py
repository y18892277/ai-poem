import pymysql
from .config import settings
import logging

logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库"""
    try:
        # 连接MySQL服务器
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            logger.info(f"Database {settings.DB_NAME} created successfully")
            
            # 使用数据库
            cursor.execute(f"USE {settings.DB_NAME}")
            
            # 在这里可以添加创建表的SQL语句
            # ...
            
        connection.commit()
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        if 'connection' in locals():
            connection.close() 