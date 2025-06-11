import httpx
from redis import Redis
import logfire
from app.core.config import get_settings
from app.models.space import SpaceRequest, SpaceResponse, UserSpace

settings = get_settings()
logfire.configure()
redis_client = Redis.from_url(settings.redis_url)


class LessonspaceService:
    def __init__(self):
        self.api_key = settings.lessonspace_api_key
        self.base_url = settings.lessonspace_api_url
        self.headers = {"Authorization": f"Organisation {self.api_key}"}

    async def get_or_create_space(self, request: SpaceRequest) -> SpaceResponse:
        space_key = f"space::{request.lesson_id}"
        cached_space = redis_client.get(space_key)

        if cached_space:
            logfire.info(
                "[LessonSpace] fetched from redis", lesson_id=request.lesson_id
            )
            return SpaceResponse.model_validate_json(cached_space)

        async with httpx.AsyncClient() as client:
            tutor_spaces = []
            space_data = None
            for tutor in request.tutors:
                response = await client.post(
                    f"{self.base_url}/spaces/launch/",
                    headers=self.headers,
                    json={
                        "id": request.lesson_id,
                        "user": {
                            "id": tutor.email,
                            "name": tutor.name,
                            "role": "tutor",
                            "leader": tutor.is_leader,
                        },
                    },
                )
                response.raise_for_status()
                tutor_data = response.json()
                if space_data is None:
                    space_data = tutor_data

                tutor_spaces.append(
                    UserSpace(
                        email=tutor.email,
                        name=tutor.name,
                        role="tutor",
                        space_url=tutor_data["client_url"],
                    )
                )

            student_spaces = []
            for student in request.students:
                response = await client.post(
                    f"{self.base_url}/spaces/launch/",
                    headers=self.headers,
                    json={
                        "id": request.lesson_id,
                        "user": {
                            "id": student.email,
                            "name": student.name,
                            "role": "student",
                            "leader": False,
                        },
                    },
                )
                response.raise_for_status()
                student_data = response.json()
                student_spaces.append(
                    UserSpace(
                        email=student.email,
                        name=student.name,
                        role="student",
                        space_url=student_data["client_url"],
                    )
                )

            space_response = SpaceResponse(
                space_id=space_data["room_id"],
                lesson_id=request.lesson_id,
                tutor_spaces=tutor_spaces,
                student_spaces=student_spaces,
            )

            redis_client.setex(
                space_key,
                86400,
                space_response.model_dump_json(),
            )

            logfire.info(
                "[LessonSpaceService] created new space", lesson_id=request.lesson_id
            )
            return space_response
