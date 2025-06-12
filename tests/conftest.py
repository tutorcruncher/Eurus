import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.api.core import get_db
from app.db.base_class import Base
import os

from app.main import app

TEST_DATABASE_URL = os.getenv(
    'TEST_DATABASE_URL', 'postgresql://postgres:waffle@localhost:5432/eurus_test'
)


@pytest.fixture(scope='session')
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    return engine


@pytest.fixture(scope='session')
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = get_test_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up the override after testing
    app.dependency_overrides.clear()
