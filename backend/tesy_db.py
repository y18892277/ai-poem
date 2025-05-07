# backend/test_db.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("数据库连接成功！")
    except Exception as e:
        print(f"数据库连接失败：{str(e)}")

if __name__ == "__main__":
    test_connection()