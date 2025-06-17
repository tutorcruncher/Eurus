from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.transcript import Feedback, Summary, Transcript
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


def get_summary(lesson_id: int, db: Session) -> Summary:
    return db.query(Summary).filter(Summary.lesson_id == lesson_id).first()


def get_feedback(lesson_id: int, db: Session) -> Feedback:
    return db.query(Feedback).filter(Feedback.lesson_id == lesson_id).first()
