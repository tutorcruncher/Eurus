import pytest
from app.dal.transcript import (
    create_transcript,
    get_transcript_by_lesson_id,
    update_transcript,
    delete_transcript,
    clear_transcripts,
    list_transcripts_by_lesson_ids,
)
from app.models.transcript import Transcript
from sqlalchemy.orm import Session
import uuid


@pytest.fixture(autouse=True)
def cleanup_db(db_session):
    """Clean up the database before and after each test."""
    clear_transcripts(db_session)
    db_session.commit()
    yield
    clear_transcripts(db_session)
    db_session.commit()


def test_create_and_get_transcript(db_session):
    """Test creating and getting a transcript."""
    lesson_id = f'test-lesson-{uuid.uuid4()}'
    transcription = [
        {
            'start_time': 0.0,
            'end_time': 5.0,
            'user': {'id': 123, 'name': 'John Smith'},
            'breakout_id': 'main',
            'text': 'Test transcription',
        }
    ]
    transcript = create_transcript(db_session, lesson_id, transcription)
    assert transcript is not None
    assert transcript.lesson_id == lesson_id
    assert transcript.transcription == transcription
    retrieved = get_transcript_by_lesson_id(db_session, lesson_id)
    assert retrieved is not None
    assert retrieved.lesson_id == lesson_id
    assert retrieved.transcription == transcription


def test_update_transcript(db_session: Session):
    """Test updating a transcript."""
    lesson_id = f'test-lesson-{uuid.uuid4()}'
    transcription = [
        {
            'start_time': 0.0,
            'end_time': 5.0,
            'user': {'id': 123, 'name': 'John Smith'},
            'breakout_id': 'main',
            'text': 'Test transcription',
        }
    ]
    transcript = create_transcript(db_session, lesson_id, transcription)
    db_session.commit()
    new_transcription = [
        {
            'start_time': 0.0,
            'end_time': 5.0,
            'user': {'id': 123, 'name': 'John Smith'},
            'breakout_id': 'main',
            'text': 'Updated transcription',
        }
    ]
    updated_transcript = update_transcript(db_session, transcript.id, new_transcription)
    assert updated_transcript is not None
    assert updated_transcript.lesson_id == lesson_id
    assert updated_transcript.transcription == new_transcription


def test_delete_transcript(db_session: Session):
    """Test deleting a transcript."""
    lesson_id = f'test-lesson-{uuid.uuid4()}'
    transcription = [
        {
            'start_time': 0.0,
            'end_time': 5.0,
            'user': {'id': 123, 'name': 'John Smith'},
            'breakout_id': 'main',
            'text': 'Test transcription',
        }
    ]
    transcript = create_transcript(db_session, lesson_id, transcription)
    db_session.commit()
    deleted = delete_transcript(db_session, transcript.id)
    db_session.commit()
    result = get_transcript_by_lesson_id(db_session, lesson_id)
    assert deleted is True
    assert result is None


def test_clear_transcripts(db_session: Session):
    """Test clearing all transcripts."""
    lesson_id1 = f'test-lesson-{uuid.uuid4()}'
    lesson_id2 = f'test-lesson-{uuid.uuid4()}'
    transcription = [
        {
            'start_time': 0.0,
            'end_time': 5.0,
            'user': {'id': 123, 'name': 'John Smith'},
            'breakout_id': 'main',
            'text': 'Test transcription',
        }
    ]
    create_transcript(db_session, lesson_id1, transcription)
    create_transcript(db_session, lesson_id2, transcription)
    db_session.commit()
    clear_transcripts(db_session)
    db_session.commit()
    transcripts = list_transcripts_by_lesson_ids(db_session, [lesson_id1, lesson_id2])
    assert len(transcripts) == 0
