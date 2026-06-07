from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class Base(DeclarativeBase):
    pass

def get_engine():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return create_engine(DATABASE_URL)

engine = get_engine() if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None