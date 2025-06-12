from fastapi import APIRouter, Depends, HTTPException
from app.models.space import SpaceRequest, SpaceResponse, TranscriptionWebhook
from app.services.lessonspace import LessonspaceService
from app.services.transcription import TranscriptionService, download_transcription

router = APIRouter(prefix="/space", tags=["space"])


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
    return {'status': 'success'}
