from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# 确保加载 .env 文件
load_dotenv()

class Settings(BaseSettings):
    # MySQL 配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "1106"
    MYSQL_DB: str = "poetry_battle"
    
 # 可选的完整数据库 URL
    DATABASE_URL: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:"
            f"{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:"
            f"{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'
         # 允许额外字段
        extra = "allow"

settings = Settings()