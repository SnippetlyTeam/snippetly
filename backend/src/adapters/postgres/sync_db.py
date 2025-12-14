from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url_sync)
SessionLocal = sessionmaker(autoflush=False, bind=engine)


def get_db_sync() -> Generator[Session, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
