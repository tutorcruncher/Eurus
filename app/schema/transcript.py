# See schema.sql for the SQL definition of the transcripts table
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, List


class User(BaseModel):
    id: int
    name: str


class TranscriptSegment(BaseModel):
    start_time: float
    end_time: float
    user: User
    breakout_id: str
    text: str


class Transcript(BaseModel):
    transcription: List[TranscriptSegment]


class TranscriptResponse(BaseModel):
    id: int
    lesson_id: str
    transcription: Transcript
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostLessonResponse(BaseModel):
    transcript: Transcript
    summary: str
    feedback: Dict[str, str]
