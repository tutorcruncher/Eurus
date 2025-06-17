# See schema.sql for the SQL definition of the transcripts table
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB


class Space(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

class UserSpace(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False)
    role: str = Field(nullable=False)
    leader: bool = Field(nullable=False)
    space_id: int = Field(foreign_key='space.id', nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

class Transcript(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transcription: Optional[list[dict]] = Field(nullable=True, sa_type=JSONB)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    space_id: int = Field(foreign_key='space.id', nullable=False)

    def __repr__(self):
        return f'<Transcript(lesson_id={self.lesson_id}, created_at={self.created_at})>'

    def to_concatonated_transcript(self):
        return '\n'.join([segment['text'] for segment in self.transcription])

    def get_user_transcript(self, user_id: int):
        return '\n'.join(
            [
                segment['text']
                for segment in self.transcription
                if segment['user']['id'] == user_id
            ]
        )
    
    def gather_user_transcripts(self) -> dict[int, dict[str, str]]:
        user_transcripts = {}
        for segment in self.transcription:
            user_id = segment["user"]["id"]
            text = segment["text"]
            role = segment["user"]["role"]
            if user_id not in user_transcripts:
                user_transcripts[user_id] = {
                    "role": role,
                    "text": text,
                }
            else:
                user_transcripts[user_id]["text"] += " " + text
        return user_transcripts


class Summary(SQLModel, table=True):
    """Genrated summary of the transcript."""

    id: int = Field(default=None, primary_key=True)
    main_text: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    transcript_id: int = Field(foreign_key='transcript.id', nullable=False)


class Feedback(SQLModel, table=True):
    """Feedback on the transcript."""

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False)
    role: str = Field(nullable=False)
    strengths: str = Field(nullable=True)
    improvements: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    transcript_id: int = Field(foreign_key='transcript.id', nullable=False)

    def for_display(self):
        return {
            'user_id': self.user_id,
            'role': self.role,
            'strengths': self.strengths,
            'improvements': self.improvements,
        }