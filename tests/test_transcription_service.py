import pytest
from unittest.mock import patch, MagicMock
import httpx
from fastapi import HTTPException
from app.services.transcription import (
    download_transcription,
    handle_webhook,
    TranscriptionService,
)
from app.models.space import TranscriptionWebhook
from app.dal.transcript import clear_transcripts, create_transcript
from app.api.core import get_db
from app.main import app
import uuid
import requests


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def cleanup_db(db_session):
    """Clean up the database before and after each test."""
    clear_transcripts(db_session)
    db_session.commit()
    yield
    clear_transcripts(db_session)
    db_session.commit()


def test_download_transcription_success():
    """Test successful transcription download."""
    test_data = [
        {
            "start_time": 0.0,
            "end_time": 5.0,
            "user": {"id": 123, "name": "John Smith"},
            "breakout_id": "main",
            "text": "Test transcription",
        }
    ]
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = test_data
        mock_get.return_value = mock_response

        result = download_transcription("https://example.com/transcription.json")
        assert result == test_data
        mock_get.assert_called_once_with("https://example.com/transcription.json")


def test_download_transcription_failure():
    """Test transcription download failure."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Download failed")
        result = download_transcription("https://example.com/transcription.json")
        assert result is None


def test_handle_webhook_success():
    """Test successful webhook handling."""
    test_data = [
        {
            "start_time": 0.0,
            "end_time": 5.0,
            "user": {"id": 123, "name": "John Smith"},
            "breakout_id": "main",
            "text": "Test transcription",
        }
    ]
    with patch("app.services.transcription.download_transcription") as mock_download:
        mock_download.return_value = test_data
        webhook = TranscriptionWebhook(
            transcriptionUrl="https://example.com/transcription.json"
        )
        lesson_id = f"test-lesson-{uuid.uuid4()}"
        result = handle_webhook(webhook, lesson_id)
        assert result is True


def test_handle_webhook_download_failure():
    """Test webhook handling with download failure."""
    with patch("app.services.transcription.download_transcription") as mock_download:
        mock_download.return_value = None
        webhook = TranscriptionWebhook(
            transcriptionUrl="https://example.com/transcription.json"
        )
        lesson_id = f"test-lesson-{uuid.uuid4()}"
        result = handle_webhook(webhook, lesson_id)
        assert result is False


@pytest.mark.asyncio
async def test_transcription_service_download_success():
    """Test successful transcription download in TranscriptionService."""
    service = TranscriptionService()
    test_data = [
        {
            "start_time": 0.0,
            "end_time": 5.0,
            "user": {"id": 123, "name": "John Smith"},
            "breakout_id": "main",
            "text": "Test transcription",
        }
    ]
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = test_data
        mock_get.return_value = mock_response

        result = await service.download_transcription(
            "https://example.com/transcription.json"
        )
        assert result == test_data


@pytest.mark.asyncio
async def test_transcription_service_download_403():
    """Test 403 error handling in TranscriptionService download."""
    service = TranscriptionService()
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = httpx.HTTPStatusError(
            "403 Forbidden",
            request=MagicMock(),
            response=MagicMock(status_code=403),
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.download_transcription(
                "https://example.com/transcription.json"
            )
        assert exc_info.value.status_code == 500
        assert "Access denied" in exc_info.value.detail


@pytest.mark.asyncio
async def test_transcription_service_download_other_error():
    """Test other error handling in TranscriptionService download."""
    service = TranscriptionService()
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("Download failed")
        with pytest.raises(HTTPException) as exc_info:
            await service.download_transcription(
                "https://example.com/transcription.json"
            )
        assert exc_info.value.status_code == 500
        assert "Failed to download transcription" in exc_info.value.detail


@pytest.mark.asyncio
async def test_transcription_service_get_transcript(db_session):
    """Test getting a transcript in TranscriptionService."""
    service = TranscriptionService()

    # Create test data
    lesson_id = f"test-lesson-{uuid.uuid4()}"
    transcription = [
        {
            "start_time": 0.0,
            "end_time": 5.0,
            "user": {"id": 123, "name": "John Smith"},
            "breakout_id": "main",
            "text": "Test transcription",
        }
    ]

    # Create transcript directly in database
    transcript = create_transcript(db_session, lesson_id, transcription)
    db_session.commit()

    # Get transcript
    result = service.get_transcript(lesson_id, db_session)
    assert result is not None
    assert result.lesson_id == lesson_id
    assert result.transcription == transcription

    # Test non-existent transcript
    with pytest.raises(HTTPException) as exc_info:
        service.get_transcript("non-existent-id", db_session)
    assert exc_info.value.status_code == 404
    assert "Transcript not found" in exc_info.value.detail
