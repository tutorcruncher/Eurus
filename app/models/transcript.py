# See schema.sql for the SQL definition of the transcripts table
from sqlalchemy import Column, String, JSON, DateTime, Integer
from datetime import datetime
from app.db.base_class import Base
from pydantic import BaseModel
from typing import Dict, Any, List


class Transcript(Base):
    __tablename__ = 'transcripts'

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(String, index=True, nullable=False)
    transcription = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f'<Transcript(lesson_id={self.lesson_id}, created_at={self.created_at})>'


class User(BaseModel):
    id: int
    name: str


class TranscriptSegment(BaseModel):
    start_time: float
    end_time: float
    user: User
    breakout_id: str
    text: str


class TranscriptResponse(BaseModel):
    id: int
    lesson_id: str
    transcription: List[TranscriptSegment]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
