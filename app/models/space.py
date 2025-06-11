from pydantic import BaseModel, Field
from typing import List


class Participant(BaseModel):
    name: str = Field(..., description="Name of the participant")
    email: str = Field(..., description="Email of the participant")


class SpaceRequest(BaseModel):
    lesson_id: str = Field(..., description="Unique identifier for the lesson")
    teachers: List[Participant] = Field(
        ..., description="List of teachers participating in the lesson"
    )
    students: List[Participant] = Field(
        ..., description="List of students participating in the lesson"
    )


class SpaceResponse(BaseModel):
    space_url: str = Field(..., description="URL to access the Lessonspace")
    space_id: str = Field(..., description="Unique identifier for the space")
    lesson_id: str = Field(
        ..., description="Lesson identifier this space is associated with"
    )
