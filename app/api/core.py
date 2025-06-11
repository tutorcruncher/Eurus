from fastapi import APIRouter, Depends
from app.models.space import SpaceRequest, SpaceResponse
from app.services.lessonspace import LessonspaceService

router = APIRouter(prefix="/space", tags=["space"])


@router.post("/", response_model=SpaceResponse)
async def create_space(
    request: SpaceRequest,
    service: LessonspaceService = Depends(LessonspaceService),
) -> SpaceResponse:
    return await service.get_or_create_space(request)
