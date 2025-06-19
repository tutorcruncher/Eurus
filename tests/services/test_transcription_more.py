import pytest
from unittest.mock import patch, AsyncMock, Mock
import httpx
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine

from app.services.transcription import TranscriptionService
from app.models.transcript import Transcript
from app.ai_tool.output_formats import SummaryOutput, ChapterOutput


@pytest.fixture
def transcription_service():
    return TranscriptionService()


@pytest.mark.asyncio
async def test_download_transcription_access_denied(transcription_service):
    """Simulate a 403 from S3 and ensure custom HTTPException is raised."""

    # Build a fake Response object with status 403
    request = httpx.Request('GET', 'http://s3/test')
    response = httpx.Response(403, request=request)

    def raise_error(*args, **kwargs):
        raise httpx.HTTPStatusError('denied', request=request, response=response)

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = raise_error

        with pytest.raises(HTTPException) as exc:
            await transcription_service.download_transcription('http://s3/test')

        assert exc.value.status_code == 500
        assert 'Access denied' in str(exc.value.detail)


@pytest.mark.asyncio
async def test_handle_webhook_generic_error(transcription_service):
    """If download_transcription raises generic exception, handle_webhook should propagate HTTPException."""

    with patch.object(
        transcription_service, 'download_transcription', side_effect=Exception('boom')
    ):
        with pytest.raises(HTTPException) as exc:
            await transcription_service.handle_webhook(
                webhook=type('W', (), {'transcriptionUrl': 'u'})(),  # minimal stub
                lesson_id='L',
                db=Session(create_engine('sqlite:///:memory:')),
            )
        assert exc.value.status_code == 500
        assert 'Failed to process transcription' in str(exc.value.detail)


def _memory_session():
    """Return a Session connected to the Postgres test database.

    A helper similar to the one in ``tests.dal.test_transcript_dal`` so any
    JSONB columns compile correctly during test runs.
    """

    import os

    db_url = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/eurus_test',
    )

    engine = create_engine(db_url, echo=False)
    SQLModel.metadata.drop_all(engine)  # type: ignore[arg-type]
    SQLModel.metadata.create_all(engine)
    return Session(engine)


@pytest.mark.asyncio
async def test_get_lesson_summary(transcription_service, monkeypatch):
    """Validate aggregation of summary/chapters/feedback."""

    lesson_id = 'sum-1'

    with _memory_session() as db:
        # Insert a dummy transcript so the DAL fetch returns object
        transcript_obj = Transcript(lesson_id=lesson_id, transcription=[])
        db.add(transcript_obj)
        db.commit()

        # Patch DAL helpers
        monkeypatch.setattr(
            'app.dal.transcript.get_transcript', lambda lesson_id, db: transcript_obj
        )
        dummy_summary_output = SummaryOutput(
            key_points='kp',
            short_summary='s' * 60,
            long_summary='l' * 1200,
            recommended_focus='r' * 60,
        )

        class DummySummary:
            def to_schema(self):
                return dummy_summary_output

        monkeypatch.setattr(
            'app.dal.transcript.get_summary', lambda l, db: DummySummary()
        )
        monkeypatch.setattr('app.dal.transcript.get_feedback', lambda l, db: [])
        monkeypatch.setattr('app.services.transcription.get_feedback', lambda l, db: [])
        monkeypatch.setattr('app.dal.transcript.get_user_spaces', lambda l, db: [])
        monkeypatch.setattr(
            'app.services.transcription.get_user_spaces', lambda l, db: []
        )

        # ChapterAgent
        async def fake_chapters(self, t):
            return [ChapterOutput(start_time='0', end_time='1', description='intro')]

        monkeypatch.setattr(
            'app.ai_tool.agents.ChapterAgent.break_down_lesson',
            fake_chapters,
        )

        monkeypatch.setattr(
            'app.services.transcription.get_summary', lambda l, db: DummySummary()
        )

        summary = await transcription_service.get_lesson_summary(lesson_id, db)

        assert summary['key_points'] == 'kp'
        assert summary['chapters'][0].description == 'intro'
