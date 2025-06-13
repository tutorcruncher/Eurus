import httpx
from redis import Redis
import logfire
from app.core.config import get_settings
from app.models.space import SpaceRequest, SpaceResponse, UserSpace
import asyncio
from fastapi import HTTPException
from app.core.dataclass import BaseRequest
from dataclasses import dataclass
from typing import Optional, Dict, Union

settings = get_settings()
logfire.configure()
redis_client = Redis.from_url(settings.redis_url)

@dataclass
class LessonSpaceRequest(BaseRequest):
    id: Union[int, str]
    user: Dict[str, Union[str, bool]]
    transcribe: bool = True
    record_av: bool = True
    webhooks: Optional[Dict] = None
    timeouts: Optional[Dict] = None


class LessonspaceService:
    def __init__(self):
        self.api_key = settings.lessonspace_api_key
        self.base_url = settings.lessonspace_api_url
        self.headers = {'Authorization': f'Organisation {self.api_key}'}

    async def _create_user_space(
        self, client, lesson_id, user, role, leader, not_before=None
    ):
        request = LessonSpaceRequest(
            id=lesson_id,
            user={
                'id': user.user_id,
                'name': user.name,
                'role': role,
                'leader': leader,
            },
            webhooks={
                'transcription': {
                    'finish': f'{settings.webhook_base_url}/api/space/webhook/transcription/{lesson_id}'
                }
            }
        )

        if not_before:
            request.timeouts = {'not_before': not_before.isoformat()}

        resp = await client.post(
            f'{self.base_url}/spaces/launch/',
            headers=self.headers,
            json=request.to_dict(),
        )
        resp.raise_for_status()
        data = resp.json()
        return UserSpace(
            user_id=user.user_id,
            name=user.name,
            role=role,
            space_url=data['client_url'],
        ), data['room_id']

    async def get_or_create_space(self, request: SpaceRequest) -> SpaceResponse:
        try:
            async with httpx.AsyncClient() as client:
                tasks = []
                for tutor in request.tutors:
                    tasks.append(
                        self._create_user_space(
                            client,
                            request.lesson_id,
                            tutor,
                            'tutor',
                            tutor.is_leader,
                            request.not_before,
                        )
                    )
                for student in request.students:
                    tasks.append(
                        self._create_user_space(
                            client,
                            request.lesson_id,
                            student,
                            'student',
                            False,
                            request.not_before,
                        )
                    )
                results = await asyncio.gather(*tasks)
                user_spaces, room_ids = zip(*results)
                tutor_spaces = [us for us in user_spaces if us.role == 'tutor']
                student_spaces = [us for us in user_spaces if us.role == 'student']
                space_id = room_ids[0] if room_ids else None
                space_response = SpaceResponse(
                    space_id=space_id,
                    lesson_id=request.lesson_id,
                    tutor_spaces=tutor_spaces,
                    student_spaces=student_spaces,
                )

                logfire.info(
                    '[LessonSpaceService] created new space',
                    lesson_id=request.lesson_id,
                    space_id=space_id,
                    tutor_count=len(tutor_spaces),
                    student_count=len(student_spaces),
                    not_before=request.not_before.isoformat()
                    if request.not_before
                    else None,
                )
                return space_response
        except Exception as e:
            logfire.error(
                '[LessonSpaceService] error in get_or_create_space',
                lesson_id=request.lesson_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=500, detail='Internal server error: ' + str(e)
            )
