import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.core.config import settings
from app.models.base import Base
from app.models.user import User
from app.models.poetry import Poetry, Battle, Season

def init_db():
    engine = create_engine(settings.get_database_url)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating initial data")
    init_db()
    print("Initial data created") 