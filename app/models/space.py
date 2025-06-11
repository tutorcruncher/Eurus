from pydantic import BaseModel, Field, EmailStr
from typing import List


class User(BaseModel):
    name: str = Field(..., description="Name of the user")
    email: EmailStr = Field(..., description="Email of the user")


class SpaceRequest(BaseModel):
    lesson_id: str = Field(..., description="Unique identifier for the lesson")
    teachers: List[User] = Field(
        ..., description="List of teachers participating in the lesson"
    )
    students: List[User] = Field(
        ..., description="List of students participating in the lesson"
    )


class UserSpace(BaseModel):
    email: EmailStr = Field(..., description="Email of the user")
    name: str = Field(..., description="Name of the user")
    role: str = Field(..., description="Role of the user (teacher/student)")
    space_url: str = Field(..., description="Unique space URL for this user")


class SpaceResponse(BaseModel):
    space_id: str = Field(..., description="Unique identifier for the space")
    lesson_id: str = Field(
        ..., description="Lesson identifier this space is associated with"
    )
    teacher_spaces: List[UserSpace] = Field(
        ..., description="List of teacher-specific space URLs"
    )
    student_spaces: List[UserSpace] = Field(
        ..., description="List of student-specific space URLs"
    )
