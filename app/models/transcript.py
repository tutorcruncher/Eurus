# See schema.sql for the SQL definition of the transcripts table
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB

from app.ai_tool.output_formats import SummaryOutput
from app.schema.transcript import FeedbackWithUserOutput


class Space(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: str = Field(index=True, nullable=False)
    lesson_space_id: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )


class UserSpaceModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False)
    role: str = Field(nullable=False)
    leader: bool = Field(nullable=False)
    lesson_id: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )


class Transcript(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transcription: Optional[list[dict]] = Field(nullable=True, sa_type=JSONB)
    lesson_id: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

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

    def gather_user_transcripts(
        self, users_lookup: dict[int, UserSpaceModel]
    ) -> dict[int, dict[str, str]]:
        user_transcripts = {}
        for segment in self.transcription:
            user_id = segment['user']['id']
            text = segment['text']
            # role = users_lookup[user_id].role
            if user_id == 3626675:
                role = 'tutor'
            else:
                role = 'student'
            if user_id not in user_transcripts:
                user_transcripts[user_id] = {
                    'text': text,
                    'role': role,
                }
            else:
                user_transcripts[user_id]['text'] += ' ' + text
        return user_transcripts


class Summary(SQLModel, table=True):
    """Genrated summary of the transcript."""

    id: int = Field(default=None, primary_key=True)
    long_summary: str = Field(nullable=True)
    short_summary: str = Field(nullable=True)
    key_points: str = Field(nullable=True)
    recommended_focus: str = Field(nullable=True)
    lesson_id: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_schema(self):
        return SummaryOutput(
            key_points=self.key_points,
            short_summary=self.short_summary,
            long_summary=self.long_summary,
            recommended_focus=self.recommended_focus,
        )


class Feedback(SQLModel, table=True):
    """Feedback on the transcript."""

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False)
    role: str = Field(nullable=False)
    strengths: str = Field(nullable=True)
    improvements: str = Field(nullable=True)
    lesson_id: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_schema(self):
        return FeedbackWithUserOutput(
            user_id=self.user_id,
            role=self.role,
            strengths=self.strengths,
            improvements=self.improvements,
        )
