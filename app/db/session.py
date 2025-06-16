from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.utils.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)

# TODO: Consider adding pooling

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
