import httpx
from redis import Redis
import logfire
from app.core.config import get_settings
from app.models.space import SpaceRequest, SpaceResponse, UserSpace
import asyncio
from fastapi import HTTPException

settings = get_settings()
logfire.configure()
redis_client = Redis.from_url(settings.redis_url)


class LessonspaceService:
    def __init__(self):
        self.api_key = settings.lessonspace_api_key
        self.base_url = settings.lessonspace_api_url
        self.headers = {"Authorization": f"Organisation {self.api_key}"}

    async def _create_user_space(self, client, lesson_id, user, role, leader):
        resp = await client.post(
            f"{self.base_url}/spaces/launch/",
            headers=self.headers,
            json={
                "id": lesson_id,
                "user": {
                    "id": user.email,
                    "name": user.name,
                    "role": role,
                    "leader": leader,
                },
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return UserSpace(
            email=user.email,
            name=user.name,
            role=role,
            space_url=data["client_url"],
        ), data["room_id"]

    async def get_or_create_space(self, request: SpaceRequest) -> SpaceResponse:
        try:
            # space_key = f"space::{request.lesson_id}"
            # cached_space = redis_client.get(space_key)

            # if cached_space:
            #     logfire.info(
            #         "[LessonSpace] fetched from redis", lesson_id=request.lesson_id
            #     )
            #     return SpaceResponse.model_validate_json(cached_space)

            async with httpx.AsyncClient() as client:
                tasks = []
                for tutor in request.tutors:
                    tasks.append(
                        self._create_user_space(
                            client, request.lesson_id, tutor, "tutor", tutor.is_leader
                        )
                    )
                for student in request.students:
                    tasks.append(
                        self._create_user_space(
                            client, request.lesson_id, student, "student", False
                        )
                    )

                results = await asyncio.gather(*tasks)
                user_spaces, room_ids = zip(*results)
                tutor_spaces = [us for us in user_spaces if us.role == "tutor"]
                student_spaces = [us for us in user_spaces if us.role == "student"]
                # All room_ids will be the same for the same lesson, so just pick the first
                space_id = room_ids[0] if room_ids else None

                space_response = SpaceResponse(
                    space_id=space_id,
                    lesson_id=request.lesson_id,
                    tutor_spaces=tutor_spaces,
                    student_spaces=student_spaces,
                )

                # redis_client.setex(
                #     space_key,
                #     86400,
                #     space_response.model_dump_json(),
                # )

                logfire.info(
                    "[LessonSpaceService] created new space",
                    lesson_id=request.lesson_id,
                    space_id=space_id,
                    tutor_count=len(tutor_spaces),
                    student_count=len(student_spaces),
                )
                return space_response
        except Exception as e:
            logfire.error(
                "[LessonSpaceService] error in get_or_create_space",
                lesson_id=request.lesson_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=500, detail="Internal server error: " + str(e)
            )
