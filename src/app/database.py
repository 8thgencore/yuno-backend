from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config import config


def get_url() -> str:
    """
    Return the SQLAlchemy connection string
    """
    return config.db.uri


def get_db():
    """
    Create a new database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


engine = create_engine(get_url())

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
