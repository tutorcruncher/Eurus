from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.transcript import Transcript
from app.db.session import SessionLocal
from datetime import datetime


def create_transcript(db: Session, lesson_id: int, transcription: dict) -> Transcript:
    transcript = Transcript(lesson_id=lesson_id, transcription=transcription)
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript


def get_transcript(lesson_id: int, db: Session) -> Transcript:
    return db.query(Transcript).filter(Transcript.lesson_id == lesson_id).first()
