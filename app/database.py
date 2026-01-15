from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import config

Base = declarative_base()
engine = create_engine(f"sqlite:///{config.sqlite_db_path}", echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
