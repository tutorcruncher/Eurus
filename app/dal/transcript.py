from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.transcript import Transcript
from app.db.session import SessionLocal
from datetime import datetime


def clear_transcripts(db: Session):
    db.query(Transcript).delete()
    db.commit()
    db.flush()


def create_transcript(db: Session, lesson_id: str, transcription: dict) -> Transcript:
    transcript = Transcript(
        lesson_id=lesson_id,
        transcription=transcription
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript


def get_transcript_by_lesson_id(db: Session, lesson_id: str) -> Optional[Transcript]:
    return db.query(Transcript).filter(Transcript.lesson_id == lesson_id).first()


def get_transcript_by_id(db: Session, transcript_id: int) -> Optional[Transcript]:
    return db.query(Transcript).filter(Transcript.id == transcript_id).first()


def list_transcripts_by_lesson_ids(db: Session, lesson_ids: List[str]) -> List[Transcript]:
    return db.query(Transcript).filter(Transcript.lesson_id.in_(lesson_ids)).all()


def update_transcript(db: Session, transcript_id: int, transcription: dict) -> Optional[Transcript]:
    """Update an existing transcript."""
    transcript = get_transcript_by_id(db, transcript_id)
    if transcript:
        transcript.transcription = transcription
        transcript.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(transcript)
    return transcript


def delete_transcript(db: Session, transcript_id: int) -> bool:
    """Delete a transcript."""
    transcript = get_transcript_by_id(db, transcript_id)
    if transcript:
        db.delete(transcript)
        db.commit()
        return True
    return False 