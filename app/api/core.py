from fastapi import APIRouter, Depends, HTTPException
from app.models.space import SpaceRequest, SpaceResponse, TranscriptionWebhook
from app.services.lessonspace import LessonspaceService
from app.services.transcription import TranscriptionService, download_transcription
from app.models.transcript import Transcript, TranscriptResponse
from app.db.session import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(prefix="/space", tags=["space"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=SpaceResponse)
async def create_space(
    request: SpaceRequest,
    service: LessonspaceService = Depends(LessonspaceService),
) -> SpaceResponse:
    return await service.get_or_create_space(request)


@router.post("/webhook/transcription/{lesson_id}")
async def handle_transcription_webhook(
    lesson_id: str,
    webhook: TranscriptionWebhook,
):
    service = TranscriptionService()
    await service.handle_webhook(webhook, lesson_id)
    return {"status": "success"}


@router.get("/transcripts/{lesson_id}", response_model=TranscriptResponse)
async def get_transcript(
    lesson_id: str,
    db: Session = Depends(get_db),
    service: TranscriptionService = Depends(TranscriptionService),
):
    """Get transcript for a lesson by ID."""
    return service.get_transcript(lesson_id, db)
