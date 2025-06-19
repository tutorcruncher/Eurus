from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from app.utils.settings import get_settings

settings = get_settings()
# The SQLModel helper "create_engine" is a thin wrapper around SQLAlchemy's
# create_engine but keeps the right typing information for SQLModel.
# Echo is enabled when running in dev mode so that SQL emitted can be
# inspected easily during development.
engine = create_engine(settings.database_url, echo=settings.dev)

# TODO: Consider adding pooling


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a SQLModel-aware session."""
    with Session(engine) as session:
        yield session
