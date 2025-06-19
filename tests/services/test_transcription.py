import pytest
from unittest.mock import patch, AsyncMock, Mock
from fastapi import HTTPException
from app.services.transcription import TranscriptionService
from app.schema.space import TranscriptionWebhook
from app.ai_tool.output_formats import SummaryOutput
from app.dal.transcript import get_transcript


@pytest.fixture
def transcription_service(settings):
    return TranscriptionService()


@pytest.fixture
def mock_transcription_data():
    return {
        'text': 'This is a test transcription',
        'words': [
            {'word': 'This', 'start': 0.0, 'end': 0.5},
            {'word': 'is', 'start': 0.5, 'end': 1.0},
            {'word': 'a', 'start': 1.0, 'end': 1.5},
            {'word': 'test', 'start': 1.5, 'end': 2.0},
            {'word': 'transcription', 'start': 2.0, 'end': 2.5},
        ],
    }


@pytest.mark.asyncio
async def test_download_transcription_success(
    transcription_service, mock_transcription_data
):
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.json = Mock(return_value=mock_transcription_data)
        mock_response.raise_for_status = Mock()
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )

        result = await transcription_service.download_transcription(
            'http://test-url.com/transcript'
        )
        assert result == mock_transcription_data


@pytest.mark.asyncio
async def test_download_transcription_403_error(transcription_service):
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 403
        mock_client.return_value.__aenter__.return_value.get.side_effect = (
            HTTPException(status_code=403, detail='Access denied')
        )

        with pytest.raises(HTTPException) as exc_info:
            await transcription_service.download_transcription(
                'http://test-url.com/transcript'
            )
        assert exc_info.value.status_code == 500
        assert 'Failed to download transcription' in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_handle_webhook_success(
    transcription_service, db_session, mock_transcription_data
):
    webhook = TranscriptionWebhook(transcriptionUrl='http://test-url.com/transcript')
    lesson_id = 'test-lesson-123'

    dummy_summary = SummaryOutput(
        key_points='kp',
        short_summary='s' * 60,
        long_summary='l' * 1200,
        recommended_focus='r' * 60,
    )

    with (
        patch.object(
            transcription_service,
            'download_transcription',
            return_value=mock_transcription_data,
        ),
        patch(
            'app.services.transcription.SummaryAgent.summarize_lesson',
            return_value=dummy_summary,
        ),
        patch(
            'app.services.transcription.StudentFeedbackAgent.provide_feedback_with_str',
            return_value=('strengths', 'improvements'),
        ),
        patch(
            'app.services.transcription.TutorFeedbackAgent.provide_feedback_with_str',
            return_value=('strengths', 'improvements'),
        ),
        patch(
            'app.dal.transcript.get_user_spaces',
            return_value=[],
        ),
        patch(
            'app.models.transcript.Transcript.gather_user_transcripts',
            return_value={},
        ),
    ):
        await transcription_service.handle_webhook(webhook, lesson_id, db_session)

        # Verify transcript was created in database via DAL helper.
        transcript = get_transcript(lesson_id, db_session)
        assert transcript is not None
        assert transcript.lesson_id == lesson_id


@pytest.mark.asyncio
async def test_get_transcript_not_found(transcription_service, db_session):
    with pytest.raises(HTTPException) as exc_info:
        await transcription_service.get_transcript_by_id(
            'non-existent-lesson', db_session
        )
    assert exc_info.value.status_code == 404
    assert 'Transcript not found' in str(exc_info.value.detail)
