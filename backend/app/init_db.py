from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models.rankings import Season, Ranking
from .models.users import User
from .models.poetry import Poetry

# 创建所有表
def init_db():
    Base.metadata.create_all(bind=engine)

def init_poetry_data(db: Session):
    """初始化诗词数据"""
    try:
        # 检查是否已有诗词数据
        if db.query(Poetry).first():
            return
        
        # 添加一些示例诗词
        sample_poetry = [
            Poetry(
                title="静夜思",
                author="李白",
                dynasty="唐",
                content="床前明月光，疑是地上霜。举头望明月，低头思故乡。",
                type="五言绝句",
                tags="思乡,月亮",
                difficulty=1
            ),
            Poetry(
                title="春晓",
                author="孟浩然",
                dynasty="唐",
                content="春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。",
                type="五言绝句",
                tags="春天,清晨",
                difficulty=1
            ),
            Poetry(
                title="登鹳雀楼",
                author="王之涣",
                dynasty="唐",
                content="白日依山尽，黄河入海流。欲穷千里目，更上一层楼。",
                type="五言绝句",
                tags="登高,壮志",
                difficulty=1
            )
        ]
        
        db.add_all(sample_poetry)
        db.commit()
        print("诗词数据初始化成功！")
    except Exception as e:
        print(f"初始化诗词数据失败: {e}")
        db.rollback()

# 初始化测试数据
def init_test_data():
    db = SessionLocal()
    try:
        # 初始化诗词数据
        init_poetry_data(db)
        
        # 创建测试用户
        test_users = [
            User(
                username=f"user{i}",
                nickname=f"用户{i}",
                email=f"user{i}@example.com",
                avatar=f"https://api.dicebear.com/7.x/adventurer/svg?seed=user{i}",
                is_admin=(i == 1)  # 第一个用户设为管理员
            )
            for i in range(1, 11)
        ]
        db.add_all(test_users)
        db.commit()

        # 创建测试赛季
        now = datetime.utcnow()
        test_seasons = [
            Season(
                name="第一赛季",
                start_time=now - timedelta(days=60),
                end_time=now - timedelta(days=30)
            ),
            Season(
                name="第二赛季",
                start_time=now - timedelta(days=29),
                end_time=now
            ),
            Season(
                name="第三赛季",
                start_time=now + timedelta(seconds=1),
                end_time=now + timedelta(days=30)
            )
        ]
        db.add_all(test_seasons)
        db.commit()

        # 创建测试排名数据
        for season in test_seasons:
            for user in test_users:
                ranking = Ranking(
                    user_id=user.id,
                    season_id=season.id,
                    score=100 + user.id * 10,
                    total_battles=20 + user.id,
                    win_count=10 + user.id // 2,
                    lose_count=10 + (user.id - 1) // 2
                )
                ranking.win_rate = (ranking.win_count / ranking.total_battles) * 100
                db.add(ranking)
        db.commit()

    except Exception as e:
        print(f"初始化测试数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("正在初始化数据库...")
    init_db()
    print("正在创建测试数据...")
    init_test_data()
    print("数据库初始化完成！") 