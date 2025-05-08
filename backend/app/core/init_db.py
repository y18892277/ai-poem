# backend/app/core/init_db.py
from sqlalchemy.orm import Session
from ..models.poetry import Poetry

def init_poetry_data(db: Session):
    """初始化诗词数据"""
    if db.query(Poetry).first():
        return
    
    poetry_data = [
        {
            "title": "静夜思",
            "author": "李白",
            "dynasty": "唐",
            "content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
            "type": "诗",
            "tags": "思乡,月亮"
        },
        # 添加更多诗词...
    ]
    
    for data in poetry_data:
        poetry = Poetry(**data)
        db.add(poetry)
    
    db.commit()