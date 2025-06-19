# See schema.sql for the SQL definition of the transcripts table
from datetime import datetime
from pydantic import BaseModel
from typing import List

from app.ai_tool.output_formats import ChapterOutput


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


class FeedbackWithUserOutput(BaseModel):
    user_id: int
    role: str
    strengths: str
    improvements: str


class PostLessonResponse(BaseModel):
    transcription: List[TranscriptSegment]
    key_points: str
    short_summary: str
    long_summary: str
    recommended_focus: str
    feedback: List[FeedbackWithUserOutput]
    chapters: list[ChapterOutput]
