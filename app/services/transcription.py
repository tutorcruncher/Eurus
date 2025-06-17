import httpx
from fastapi import HTTPException
from app.utils.settings import get_settings
from app.schema.space import TranscriptionWebhook
from app.dal.transcript import (
    create_feedback,
    create_summary,
    create_transcript,
    get_feedback,
    get_summary,
    get_transcript,
)
from app.models.transcript import Transcript
from sqlmodel import Session
from app.ai_tool.agents import StudentFeedbackAgent, SummaryAgent, TutorFeedbackAgent
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
        
        summary = await SummaryAgent().summarize_lesson(transcript)
        create_summary(db, transcript.id, summary)

        user_transcripts = transcript.gather_user_transcripts()
        for user_id, user_transcript in user_transcripts.items():
            if user_transcript["role"] == "tutor":
                tutor_feedback = await TutorFeedbackAgent().provide_feedback_with_str(user_transcript["text"])
            else:
                student_feedback = await StudentFeedbackAgent().provide_feedback_with_str(user_transcript["text"])
            create_feedback(db, transcript.id, user_id, user_transcript["role"], tutor_feedback, student_feedback)

    async def get_transcript_by_id(self, lesson_id: str, db: Session) -> Transcript:
        transcript = get_transcript(lesson_id, db)
        if not transcript:
            raise HTTPException(
                status_code=404,
                detail=f'Transcript not found for lesson ID: {lesson_id}',
            )

    async def get_lesson_summary(self, lesson_id: str, db: Session) -> dict[str, list]:
        if transcript := get_transcript(lesson_id, db):
            transcript = transcript.transcription

        if summary := get_summary(lesson_id, db):
            summary = summary.main_text

        if feedback := get_feedback(lesson_id, db):
            feedback = {
                'tutor_strengths': feedback.tutor_strengths,
                'tutor_improvements': feedback.tutor_improvements,
                'student_strengths': feedback.student_strengths,
                'student_improvements': feedback.student_improvements,
            }

        return {
            'transcript': transcript,
            'summary': summary,
            'feedback': feedback,
        }
