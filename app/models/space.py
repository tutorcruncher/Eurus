from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Union
from datetime import datetime


class User(BaseModel):
    user_id: Union[int, str] = Field(..., description="Unique identifier for the user")
    name: str = Field(..., description="Name of the user")
    email: Optional[EmailStr] = Field(None, description="Email of the user")


class LeaderUser(User):
    is_leader: bool = Field(True, description="Whether the user is a leader")


class SpaceRequest(BaseModel):
    lesson_id: int | str = Field(..., description="Unique identifier for the lesson")
    tutors: List[LeaderUser] = Field(
        ..., description="List of tutors participating in the lesson"
    )
    students: List[User] = Field(
        ..., description="List of students participating in the lesson"
    )
    not_before: Optional[datetime] = Field(
        None,
        description="Earliest time that users can join the space. If not set, users can join immediately.",
    )


class UserSpace(BaseModel):
    user_id: Union[int, str] = Field(..., description="Unique identifier for the user")
    name: str = Field(..., description="Name of the user")
    role: str = Field(..., description="Role of the user (tutor/student)")
    space_url: str = Field(..., description="Unique space URL for this user")


class SpaceResponse(BaseModel):
    space_id: int | str = Field(..., description="Unique identifier for the space")
    lesson_id: int | str = Field(
        ..., description="Lesson identifier this space is associated with"
    )
    tutor_spaces: List[UserSpace] = Field(
        ..., description="List of tutor-specific space URLs"
    )
    student_spaces: List[UserSpace] = Field(
        ..., description="List of student-specific space URLs"
    )
