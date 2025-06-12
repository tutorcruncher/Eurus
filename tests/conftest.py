import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
import os

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
