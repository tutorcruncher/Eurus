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
                f"{self.base_url}/spaces/launch/",
                headers=self.headers,
                json={
                    "id": request.lesson_id,
                    "user": {
                        "id": first_teacher.email,
                        "name": first_teacher.name,
                        "role": "teacher",
                        "leader": True,
                    },
                },
            )
            response.raise_for_status()
            space_data = response.json()

            # Store teacher's space URL
            teacher_spaces = [
                UserSpace(
                    email=first_teacher.email,
                    name=first_teacher.name,
                    role="teacher",
                    space_url=space_data["client_url"],
                )
            ]

            # Add remaining teachers
            for teacher in request.teachers[1:]:
                response = await client.post(
                    f"{self.base_url}/spaces/launch/",
                    headers=self.headers,
                    json={
                        "id": request.lesson_id,
                        "user": {
                            "id": teacher.email,
                            "name": teacher.name,
                            "role": "teacher",
                            "leader": False,
                        },
                    },
                )
                response.raise_for_status()
                teacher_data = response.json()
                teacher_spaces.append(
                    UserSpace(
                        email=teacher.email,
                        name=teacher.name,
                        role="teacher",
                        space_url=teacher_data["client_url"],
                    )
                )

            # Add students
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
                teacher_spaces=teacher_spaces,
                student_spaces=student_spaces,
            )

            # Cache the space
            redis_client.setex(
                space_key,
                86400,  # 24 hours
                space_response.model_dump_json(),
            )

            logfire.info("Created new space", lesson_id=request.lesson_id)
            return space_response
