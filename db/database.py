"""Database configurations"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = 'sqlite:///./social.db'

db_engine = create_engine(DB_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=db_engine
)

Base = declarative_base()


def get_db():
    """Getting DB to run and close"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
