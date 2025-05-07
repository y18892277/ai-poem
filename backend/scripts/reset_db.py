import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.models.base import Base
from app.models.user import User
from app.models.poetry import Poetry, Battle, Season

def reset_db():
    try:
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        print("所有表已删除")
        
        # 重新创建所有表
        Base.metadata.create_all(bind=engine)
        print("所有表已重新创建")
    except Exception as e:
        print(f"数据库重置失败：{str(e)}")
        raise

if __name__ == "__main__":
    reset_db()