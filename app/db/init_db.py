from sqlalchemy import create_engine
from app.db.base_class import Base
from app.models.transcript import Transcript
from app.core.config import get_settings

settings = get_settings()


def init_db() -> None:
    """Initialize the database by creating all tables."""
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    print('Creating database tables...')
    init_db()
    print('Database tables created successfully!')
