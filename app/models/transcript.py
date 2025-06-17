# See schema.sql for the SQL definition of the transcripts table
from typing import Optional
from sqlmodel import Field, SQLModel, String, JSON, DateTime, Integer
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB


class Transcript(SQLModel, table=True):
    __tablename__ = 'transcripts'

    id: int = Field(default=None, primary_key=True)
    lesson_id: str = Field(index=True, nullable=False)
    transcription: Optional[dict] = Field(nullable=True, sa_type=JSONB)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Transcript(lesson_id={self.lesson_id}, created_at={self.created_at})>'

    def to_concatonated_transcript(self):
        return '\n'.join([segment.text for segment in self.transcription])

    def get_user_transcript(self, user_id: int):
        return '\n'.join(
            [
                segment.text
                for segment in self.transcription
                if segment.user['id'] == user_id
            ]
        )


class Summary(SQLModel, table=True):
    """Genrated summary of the transcript."""

    id: int = Field(default=None, primary_key=True)
    main_text: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    transcript_id: int = Field(foreign_key='transcripts.id', nullable=False)


class Feedback(SQLModel, table=True):
    """Feedback on the transcript."""

    id: int = Field(default=None, primary_key=True)
    tutor_feedback: str = Field(nullable=True)
    student_feedback: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    transcript_id: int = Field(foreign_key='transcripts.id', nullable=False)
