from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://mealapp:change_me@localhost:5432/mealrec")
#sqlite:///mealrec.db
#

engine = create_engine(DB_URL, echo=False, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()