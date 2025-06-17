import httpx
from fastapi import HTTPException
from app.utils.settings import get_settings
from app.schema.space import TranscriptionWebhook
from app.dal.transcript import create_transcript, get_feedback, get_summary
from app.db.session import SessionLocal
import logfire
from app.models.transcript import Transcript
from app.dal.transcript import create_transcript, get_transcript
from sqlalchemy.orm import Session
from app.ai_tool.agents import StudentFeedbackAgent, SummaryAgent, TutorFeedbackAgent
from app.models.transcript import Transcript
from app.utils.logging import logger

settings = get_settings()


class TranscriptionService:
    def __init__(self):
        self.api_key = settings.lessonspace_api_key
        self.base_url = settings.lessonspace_api_url
        self.headers = {'Authorization': f'Organisation {self.api_key}'}

    async def download_transcription(self, transcription_url: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(transcription_url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.error(
                    '[TranscriptionService] S3 access denied',
                    error=str(e),
                    url=transcription_url,
                )
                raise HTTPException(
                    status_code=500,
                    detail='Access denied to transcription file. Please check S3 permissions.',
                )
            logger.error(
                '[TranscriptionService] error downloading transcription',
                error=str(e),
                url=transcription_url,
            )
            raise HTTPException(
                status_code=500, detail='Failed to download transcription: ' + str(e)
            )
        except Exception as e:
            logger.error(
                '[TranscriptionService] error downloading transcription',
                error=str(e),
                url=transcription_url,
            )
            raise HTTPException(
                status_code=500, detail='Failed to download transcription: ' + str(e)
            )

    async def create_summary(self, transcript: Transcript) -> str:
        summary = SummaryAgent().summarize_lesson(transcript)
        return summary

    async def create_tutor_feedback(self, transcript: Transcript) -> str:
        feedback = TutorFeedbackAgent().provide_feedback(transcript)
        return feedback

    async def create_student_feedback(self, transcript: Transcript) -> str:
        feedback = StudentFeedbackAgent().provide_feedback(transcript)
        return feedback

    async def handle_webhook(
        self, webhook: TranscriptionWebhook, lesson_id: str, db: Session
    ) -> None:
        try:
            transcription_data = await self.download_transcription(
                webhook.transcriptionUrl
            )
            transcript = create_transcript(db, lesson_id, transcription_data)
            logger.info(
                '[TranscriptionService] stored transcription',
                lesson_id=lesson_id,
                transcript_id=transcript.id,
                transcription_length=len(transcription_data),
            )
        except Exception as e:
            logger.error(
                '[TranscriptionService] error handling webhook',
                error=str(e),
                lesson_id=lesson_id,
            )
            raise HTTPException(
                status_code=500, detail='Failed to process transcription: ' + str(e)
            )

    async def get_transcript_by_id(self, lesson_id: int, db: Session) -> Transcript:
        transcript = get_transcript(lesson_id, db)
        if not transcript:
            raise HTTPException(
                status_code=404,
                detail=f'Transcript not found for lesson ID: {lesson_id}',
            )

    async def post_lesson(self, lesson_id: int, db: Session) -> dict[str, list]:
        if transcript := get_transcript(lesson_id, db):
            transcript = transcript.transcription

        if summary := get_summary(lesson_id, db):
            summary = summary.main_text

        if feedback := get_feedback(lesson_id, db):
            feedback = {
                'tutor_feedback': feedback.tutor_feedback,
                'student_feedback': feedback.student_feedback,
            }

        return {
            'transcript': transcript,
            'summary': summary,
            'feedback': feedback,
        }
