from .base import Base
from .user import User
from .poetry import Poetry, UserFavoritePoetry
from .battle import Battle
from .season import Season

# 确保所有模型都被导入，这样 SQLAlchemy 才能正确创建表
__all__ = ['Base', 'User', 'Poetry', 'Battle', 'Season', 'UserFavoritePoetry']

# 导入所有模型以确保它们被注册
models = [User, Poetry, Battle, Season, UserFavoritePoetry]

# SQLAlchemy会自动处理模型注册，不需要手动操作metadata