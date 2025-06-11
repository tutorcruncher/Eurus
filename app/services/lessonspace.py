import httpx
from redis import Redis
import logfire
from app.core.config import get_settings
from app.models.space import SpaceRequest, SpaceResponse

settings = get_settings()
logfire.configure()
redis_client = Redis.from_url(settings.redis_url)


class LessonspaceService:
    def __init__(self):
        self.api_key = settings.lessonspace_api_key
        self.base_url = settings.lessonspace_api_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def get_or_create_space(self, request: SpaceRequest) -> SpaceResponse:
        # Check if space exists in Redis
        space_key = f"lessonspace:{request.lesson_id}"
        cached_space = redis_client.get(space_key)

        if cached_space:
            logfire.info("Retrieved space from cache", lesson_id=request.lesson_id)
            return SpaceResponse.model_validate_json(cached_space)

        # Create new space
        async with httpx.AsyncClient() as client:
            # Create space with first teacher as leader
            first_teacher = request.teachers[0]
            response = await client.post(
                f"{self.base_url}/v2/spaces/launch/",
                headers=self.headers,
                json={
                    "id": request.lesson_id,
                    "user": {
                        "id": first_teacher.email,
                        "name": first_teacher.name,
                        "role": "teacher",
                        "leader": True
                    }
                },
            )
            response.raise_for_status()
            space_data = response.json()

            # Add remaining teachers
            for teacher in request.teachers[1:]:
                await client.post(
                    f"{self.base_url}/v2/spaces/launch/",
                    headers=self.headers,
                    json={
                        "id": request.lesson_id,
                        "user": {
                            "id": teacher.email,
                            "name": teacher.name,
                            "role": "teacher",
                            "leader": False
                        }
                    },
                )

            # Add students
            for student in request.students:
                await client.post(
                    f"{self.base_url}/v2/spaces/launch/",
                    headers=self.headers,
                    json={
                        "id": request.lesson_id,
                        "user": {
                            "id": student.email,
                            "name": student.name,
                            "role": "student",
                            "leader": False
                        }
                    },
                )

            space_response = SpaceResponse(
                space_url=space_data["client_url"],
                space_id=space_data["room_id"],
                lesson_id=request.lesson_id,
            )

            # Cache the space
            redis_client.setex(
                space_key,
                86400,  # 24 hours
                space_response.model_dump_json(),
            )

            logfire.info("Created new space", lesson_id=request.lesson_id)
            return space_response
