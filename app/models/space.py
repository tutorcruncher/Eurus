from pydantic import BaseModel, Field


class SpaceRequest(BaseModel):
    lesson_id: str = Field(..., description='Unique identifier for the lesson')
    teacher_name: str = Field(..., description='Name of the teacher')
    student_name: str = Field(..., description='Name of the student')


class SpaceResponse(BaseModel):
    space_url: str = Field(..., description='URL to access the Lessonspace')
    space_id: str = Field(..., description='Unique identifier for the space')
    lesson_id: str = Field(..., description='Lesson identifier this space is associated with') 