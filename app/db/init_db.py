from sqlmodel import create_engine
from sqlmodel import SQLModel
from ..utils.settings import get_settings
from ..utils.logging import logger

settings = get_settings()


def init_db() -> None:
    engine = create_engine(settings.database_url, echo=True)
    SQLModel.metadata.create_all(bind=engine)


if __name__ == '__main__':
    logger.info('Creating database tables...')
    init_db()
    logger.info('Creating database tables...')
