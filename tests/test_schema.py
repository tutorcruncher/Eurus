import pytest
from sqlalchemy import inspect, text
from app.db.base_class import Base
from app.models.transcript import Transcript
import datetime
from sqlalchemy.schema import PrimaryKeyConstraint

def test_orm_matches_schema():
    """Test that the ORM models match the schema defined in schema.sql"""
    # Get the inspector from the model metadata
    metadata = Base.metadata
    
    # Get table info from ORM
    table = metadata.tables['transcripts']
    
    # Verify columns
    assert len(table.columns) == 5  # id, lesson_id, transcription, created_at, updated_at
    
    # Verify primary key
    id_column = table.columns['id']
    assert id_column.primary_key is True
    assert isinstance(id_column.type.python_type, type(int))
    
    # Verify lesson_id column
    lesson_id_column = table.columns['lesson_id']
    assert lesson_id_column.nullable is False
    assert isinstance(lesson_id_column.type.python_type, type(str))
    
    # Verify transcription column
    transcription_column = table.columns['transcription']
    assert transcription_column.nullable is False
    assert isinstance(transcription_column.type.python_type, type(dict))
    
    # Verify timestamps
    created_at_column = table.columns['created_at']
    assert created_at_column.nullable is False
    assert isinstance(created_at_column.type.python_type, type(datetime.datetime))
    
    updated_at_column = table.columns['updated_at']
    assert updated_at_column.nullable is False
    assert isinstance(updated_at_column.type.python_type, type(datetime.datetime))
    
    # Verify only primary key constraint exists
    pk_constraints = [cons for cons in table.constraints if isinstance(cons, PrimaryKeyConstraint)]
    assert len(pk_constraints) == 1
    pk_constraint = pk_constraints[0]
    assert [col.name for col in pk_constraint.columns] == ['id'] 