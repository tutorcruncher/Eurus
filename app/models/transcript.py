from sqlalchemy import Column, String, JSON, DateTime, Integer
from datetime import datetime
from app.db.base_class import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(String, index=True, nullable=False)
    transcription = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<Transcript(lesson_id={self.lesson_id}, created_at={self.created_at})>"
