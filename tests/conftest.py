import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.core.config import get_settings

# Get test database URL
settings = get_settings()
TEST_DATABASE_URL = settings.database_url + '_test'

# Create test engine and session
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope='session')
def db_engine():
    """Create a test database engine."""
    # Create test database tables
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Drop test database tables
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope='function')
def db_session(db_engine):
    """Create a test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close() 