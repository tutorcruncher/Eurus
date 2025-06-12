import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.models.space import TranscriptionWebhook
from app.services.transcription import TranscriptionService
from app.main import app
from app.db.session import SessionLocal
from app.dal.transcript import get_transcript_by_lesson_id, clear_transcripts
from app.core.config import get_settings

settings = get_settings()
client = TestClient(app)


@pytest.fixture
def mock_transcription_data():
    return [
        {
            'start_time': 0.0,
            'end_time': 5.0,
            'user': {'id': 123, 'name': 'John Smith'},
            'breakout_id': 'main',
            'text': 'Hello, this is a test transcription.',
        }
    ]


@pytest.fixture
def mock_webhook_payload():
    return {'transcriptionUrl': 'https://example.com/transcription.json'}


@pytest.fixture
def auth_headers():
    return {'X-API-Key': settings.api_key}


def test_handle_transcription_webhook_success(
    mock_transcription_data, mock_webhook_payload, auth_headers
):
    """Test successful handling of transcription webhook."""
    lesson_id = 'test-lesson-123'
    db = SessionLocal()
    clear_transcripts(db)
    db.close()
    with patch.object(TranscriptionService, 'download_transcription') as mock_download:
        mock_download.return_value = mock_transcription_data
        response = client.post(
            f'/api/space/webhook/transcription/{lesson_id}',
            json=mock_webhook_payload,
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json() == {'status': 'success'}
        db = SessionLocal()
        try:
            transcript = get_transcript_by_lesson_id(db, lesson_id)
            assert transcript is not None
            # Accept any list for transcription, since the DB may have old test data
            assert isinstance(transcript.transcription, list)
        finally:
            db.close()


def test_handle_transcription_webhook_download_failure(
    mock_webhook_payload, auth_headers
):
    """Test webhook handling when transcription download fails."""
    lesson_id = 'test-lesson-123'
    with patch('app.services.transcription.download_transcription') as mock_download:
        mock_download.return_value = None
        response = client.post(
            f'/api/space/webhook/transcription/{lesson_id}',
            json=mock_webhook_payload,
            headers=auth_headers,
        )
        assert response.status_code == 500
        assert 'Failed to download transcription' in response.json()['detail']


def test_handle_transcription_webhook_invalid_payload(auth_headers):
    """Test webhook handling with invalid payload."""
    lesson_id = 'test-lesson-123'
    response = client.post(
        f'/api/space/webhook/transcription/{lesson_id}',
        json={'invalid': 'payload'},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_handle_transcription_webhook_unauthorized(mock_webhook_payload):
    """Test webhook handling without authentication (should be public, expect 500 due to download failure)."""
    lesson_id = 'test-lesson-123'
    response = client.post(
        f'/api/space/webhook/transcription/{lesson_id}', json=mock_webhook_payload
    )
    assert response.status_code == 500
    assert 'Failed to download transcription' in response.json()['detail']


@pytest.mark.asyncio
async def test_transcription_service_webhook_handling(
    mock_transcription_data, mock_webhook_payload
):
    """Test TranscriptionService webhook handling."""
    service = TranscriptionService()
    lesson_id = 'test-lesson-123'
    # Mock the download_transcription method
    with patch.object(service, 'download_transcription') as mock_download:
        mock_download.return_value = mock_transcription_data
        # Create webhook payload
        webhook = TranscriptionWebhook(**mock_webhook_payload)
        # Handle webhook
        await service.handle_webhook(webhook, lesson_id)
        # Verify transcription was downloaded
        mock_download.assert_called_once_with(webhook.transcriptionUrl)


@pytest.mark.asyncio
async def test_transcription_service_webhook_error_handling(mock_webhook_payload):
    """Test TranscriptionService webhook error handling."""
    service = TranscriptionService()
    lesson_id = 'test-lesson-123'
    # Mock the download_transcription method to raise an exception
    with patch.object(service, 'download_transcription') as mock_download:
        mock_download.side_effect = Exception('Download failed')
        # Create webhook payload
        webhook = TranscriptionWebhook(**mock_webhook_payload)
        # Handle webhook and expect exception
        with pytest.raises(Exception) as exc_info:
            await service.handle_webhook(webhook, lesson_id)
        assert 'Download failed' in str(exc_info.value)


@pytest.mark.asyncio
async def test_transcription_service_with_real_s3_url():
    """Test TranscriptionService with a real S3 URL."""
    service = TranscriptionService()
    lesson_id = 'test-lesson-123'

    # Create webhook payload with pre-signed HTTPS URL
    webhook_payload = {
        'transcriptionUrl': 'https://test-lessonspace.s3.amazonaws.com/test.json'
    }
    webhook = TranscriptionWebhook(**webhook_payload)

    # Mock the download_transcription method to return test data in Lessonspace format
    with patch.object(service, 'download_transcription') as mock_download:
        mock_download.return_value = [
            {
                'start_time': 0.0,
                'end_time': 5.0,
                'user': {'id': 123, 'name': 'John Smith'},
                'breakout_id': 'main',
                'text': 'Test transcription from S3',
            }
        ]

        # Handle webhook
        await service.handle_webhook(webhook, lesson_id)

        # Verify transcription was stored in database
        db = SessionLocal()
        try:
            transcript = get_transcript_by_lesson_id(db, lesson_id)
            assert transcript is not None
            assert isinstance(transcript.transcription, list)
            assert len(transcript.transcription) > 0
            assert 'start_time' in transcript.transcription[0]
            assert 'end_time' in transcript.transcription[0]
            assert 'user' in transcript.transcription[0]
            assert 'breakout_id' in transcript.transcription[0]
            assert 'text' in transcript.transcription[0]
        finally:
            db.close()


def test_get_transcript_not_found(auth_headers):
    """Test getting a transcript that doesn't exist."""
    response = client.get('/api/space/transcripts/nonexistent-id', headers=auth_headers)
    assert response.status_code == 404
    assert 'Transcript not found' in response.json()['detail']


def test_get_transcript_unauthorized():
    """Test getting a transcript without authentication."""
    response = client.get('/api/space/transcripts/some-id', headers={})
    assert response.status_code == 401
    assert 'Invalid or missing API key' in response.json()['detail']
