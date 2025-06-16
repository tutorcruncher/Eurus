from sqlalchemy import create_engine
from app.db.base_class import Base
from app.models.transcript import Transcript
from app.utils.config import get_settings
from app.utils.logging import logger

settings = get_settings()


def init_db() -> None:
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    logger.info('Creating database tables...')
    init_db()
    logger.info('Creating database tables...')
