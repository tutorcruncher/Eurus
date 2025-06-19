import types
import pytest
from unittest.mock import MagicMock


def test_base_class_tablename_import():
    from app.db.base_class import Base

    class Example(Base):
        __abstract__ = True

    # SQLAlchemy would create table name lowercased
    assert Example.__tablename__ == 'example'


def test_init_db_monkeypatched(monkeypatch):
    """Ensure init_db executes without touching real database."""
    from app.db import init_db as init_module
    from sqlmodel import SQLModel

    # Monkey-patch settings to use SQLite memory URL.
    monkeypatch.setattr(
        init_module,
        'settings',
        types.SimpleNamespace(database_url='sqlite:///:memory:'),
    )

    # Replace create_engine with dummy that returns object having "dispose".
    monkeypatch.setattr(
        init_module, 'create_engine', lambda *a, **k: types.SimpleNamespace()
    )

    # Replace SQLModel.metadata.create_all to no-op and capture call.
    called = {}

    def fake_create_all(bind=None):
        called['yes'] = True

    monkeypatch.setattr(SQLModel.metadata, 'create_all', fake_create_all)

    init_module.init_db()

    assert called.get('yes') is True
