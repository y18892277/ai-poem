from pydantic import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "诗词接龙擂台赛"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT设置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 数据库设置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DB: str = "poetry_battle"
    
    # 数据库URL
    SQLALCHEMY_DATABASE_URL: Optional[str] = None
    
    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URL:
            return self.SQLALCHEMY_DATABASE_URL
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 