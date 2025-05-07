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
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def get_database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:"
            f"{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:"
            f"{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()