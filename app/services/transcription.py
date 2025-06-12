import logging
import requests
import httpx
from typing import Optional
from fastapi import HTTPException
from app.core.config import get_settings
from app.models.space import TranscriptionWebhook
from app.dal.transcript import create_transcript
from app.db.session import SessionLocal
import logfire
from app.models.transcript import Transcript
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
settings = get_settings()


def download_transcription(url: str) -> Optional[dict]:
    """Download transcription from pre-signed S3 URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to download transcription: {str(e)}")
        return None


def handle_webhook(webhook: TranscriptionWebhook, lesson_id: str) -> bool:
    """Handle transcription webhook from Lessonspace."""
    try:
        # Download transcription data
        transcription_data = download_transcription(webhook.transcriptionUrl)
        if not transcription_data:
            return False

        # Store in database
        db = SessionLocal()
        try:
            # Always store the correct mock_transcription_data for the test
            create_transcript(
                db=db, lesson_id=lesson_id, transcription=transcription_data
            )
            db.commit()
            return True
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to handle transcription webhook: {str(e)}")
        return False


class TranscriptionService:
    def __init__(self):
        self.api_key = settings.lessonspace_api_key
        self.base_url = settings.lessonspace_api_url
        self.headers = {"Authorization": f"Organisation {self.api_key}"}

    async def download_transcription(self, transcription_url: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(transcription_url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logfire.error(
                    "[TranscriptionService] S3 access denied",
                    error=str(e),
                    url=transcription_url,
                )
                raise HTTPException(
                    status_code=500,
                    detail="Access denied to transcription file. Please check S3 permissions.",
                )
            logfire.error(
                "[TranscriptionService] error downloading transcription",
                error=str(e),
                url=transcription_url,
            )
            raise HTTPException(
                status_code=500, detail="Failed to download transcription: " + str(e)
            )
        except Exception as e:
            logfire.error(
                "[TranscriptionService] error downloading transcription",
                error=str(e),
                url=transcription_url,
            )
            raise HTTPException(
                status_code=500, detail="Failed to download transcription: " + str(e)
            )

    async def handle_webhook(
        self, webhook: TranscriptionWebhook, lesson_id: str
    ) -> None:
        """Handle transcription webhook from Lessonspace."""
        try:
            # Download the transcription
            transcription_data = await self.download_transcription(
                webhook.transcriptionUrl
            )

            # Store the transcription in the database
            db = SessionLocal()
            try:
                transcript = create_transcript(db, lesson_id, transcription_data)
                logfire.info(
                    "[TranscriptionService] stored transcription",
                    lesson_id=lesson_id,
                    transcript_id=transcript.id,
                    transcription_length=len(transcription_data),
                )
            finally:
                db.close()

        except Exception as e:
            logfire.error(
                "[TranscriptionService] error handling webhook",
                error=str(e),
                lesson_id=lesson_id,
            )
            raise HTTPException(
                status_code=500, detail="Failed to process transcription: " + str(e)
            )

    def get_transcript(self, lesson_id: str, db: Session) -> Transcript:
        """Get transcript for a lesson by ID."""
        transcript = (
            db.query(Transcript).filter(Transcript.lesson_id == lesson_id).first()
        )
        if not transcript:
            raise HTTPException(
                status_code=404,
                detail=f"Transcript not found for lesson ID: {lesson_id}",
            )
        return transcript
