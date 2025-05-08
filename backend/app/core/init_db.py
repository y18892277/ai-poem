# backend/app/core/init_db.py
from sqlalchemy.orm import Session
from ..models.poetry import Poetry
from datetime import datetime, timedelta
from ..models import Season

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
            "tags": "思乡,月亮",
            "difficulty": 1
        },
        {
            "title": "春晓",
            "author": "孟浩然",
            "dynasty": "唐",
            "content": "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。",
            "type": "诗",
            "tags": "春天,自然",
            "difficulty": 1
        },
        {
            "title": "登鹳雀楼",
            "author": "王之涣",
            "dynasty": "唐",
            "content": "白日依山尽，黄河入海流。欲穷千里目，更上一层楼。",
            "type": "诗",
            "tags": "登高,壮志",
            "difficulty": 1
        },
        {
            "title": "望庐山瀑布",
            "author": "李白",
            "dynasty": "唐",
            "content": "日照香炉生紫烟，遥看瀑布挂前川。飞流直下三千尺，疑是银河落九天。",
            "type": "诗",
            "tags": "山水,壮观",
            "difficulty": 2
        },
        {
            "title": "江雪",
            "author": "柳宗元",
            "dynasty": "唐",
            "content": "千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。",
            "type": "诗",
            "tags": "冬天,孤独",
            "difficulty": 1
        },
        {
            "title": "咏柳",
            "author": "贺知章",
            "dynasty": "唐",
            "content": "碧玉妆成一树高，万条垂下绿丝绦。不知细叶谁裁出，二月春风似剪刀。",
            "type": "诗",
            "tags": "春天,柳树",
            "difficulty": 2
        },
        {
            "title": "登高",
            "author": "杜甫",
            "dynasty": "唐",
            "content": "风急天高猿啸哀，渚清沙白鸟飞回。无边落木萧萧下，不尽长江滚滚来。",
            "type": "诗",
            "tags": "秋天,登高",
            "difficulty": 2
        },
        {
            "title": "相思",
            "author": "王维",
            "dynasty": "唐",
            "content": "红豆生南国，春来发几枝。愿君多采撷，此物最相思。",
            "type": "诗",
            "tags": "爱情,相思",
            "difficulty": 1
        },
        {
            "title": "山居秋暝",
            "author": "王维",
            "dynasty": "唐",
            "content": "空山新雨后，天气晚来秋。明月松间照，清泉石上流。",
            "type": "诗",
            "tags": "秋天,山水",
            "difficulty": 1
        },
        {
            "title": "鹿柴",
            "author": "王维",
            "dynasty": "唐",
            "content": "空山不见人，但闻人语响。返景入深林，复照青苔上。",
            "type": "诗",
            "tags": "山水,禅意",
            "difficulty": 2
        }
    ]
    
    for data in poetry_data:
        poetry = Poetry(**data)
        db.add(poetry)
    
    db.commit()

def init_season_data(db: Session):
    """初始化赛季数据"""
    # 检查是否已有赛季数据
    if db.query(Season).first():
        return
    
    # 创建第一个赛季
    current_time = datetime.now()
    first_season = Season(
        name="第一赛季",
        start_date=current_time,
        end_date=current_time + timedelta(days=30),
        status="active"
    )
    
    db.add(first_season)
    db.commit()