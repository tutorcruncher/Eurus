from fastapi import APIRouter, Depends
from app.schema.lesson_planning import LessonPlanResponse, LessonSequenceResponse
from app.schema.space import SpaceRequest, SpaceResponse, TranscriptionWebhook
from app.schema.transcript import PostLessonResponse
from app.services.lesson_planning import LessonPlanService, LessonSequenceService
from app.services.lessonspace import LessonspaceService
from app.services.transcription import TranscriptionService
from app.schema.transcript import TranscriptResponse
from app.db.session import get_db
from sqlmodel import Session

router = APIRouter(prefix='/api/space', tags=['space'])


@router.post('/', response_model=SpaceResponse)
async def create_space(
    request: SpaceRequest,
    db: Session = Depends(get_db),
    service: LessonspaceService = Depends(LessonspaceService),
) -> SpaceResponse:
    return await service.get_or_create_space(request, db)


@router.post('/webhook/transcription/{lesson_id}')
async def handle_transcription_webhook(
    lesson_id: str,
    webhook: TranscriptionWebhook,
    db: Session = Depends(get_db),
):
    service = TranscriptionService()
    await service.handle_webhook(webhook, lesson_id, db)
    return {'status': 'success'}


@router.get('/transcripts/{lesson_id}', response_model=TranscriptResponse)
async def get_transcript(
    lesson_id: str,
    db: Session = Depends(get_db),
    service: TranscriptionService = Depends(TranscriptionService),
):
    return await service.get_transcript_by_id(lesson_id, db)


@router.get('/lesson-summary/{lesson_id}', response_model=PostLessonResponse)
async def get_lesson_summary(
    lesson_id: str,
    db: Session = Depends(get_db),
    service: TranscriptionService = Depends(TranscriptionService),
):
    return await service.get_lesson_summary(lesson_id, db)


@router.post('/create-lesson-plan', response_model=LessonPlanResponse)
async def create_lesson_plan(
    lesson_info: dict,
    db: Session = Depends(get_db),
    service: LessonPlanService = Depends(LessonPlanService),
):
    lesson_plan = await service.create_lesson_plan(lesson_info)
    return LessonPlanResponse(lesson_plan=lesson_plan)


@router.post('/create-lesson-sequence', response_model=LessonSequenceResponse)
async def create_lesson_sequence(
    lesson_info: dict,
    db: Session = Depends(get_db),
    service: LessonSequenceService = Depends(LessonSequenceService),
):
    return await service.create_lesson_sequence(lesson_info)
