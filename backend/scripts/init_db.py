import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.models.base import Base
from app.models.user import User
from app.models.poetry import Poetry, Battle

def init_db():
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功！")
    except Exception as e:
        print(f"数据库表创建失败：{str(e)}")
        raise

if __name__ == "__main__":
    init_db()