from typing import Generator
from app.db.session import get_session
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    return get_session()
