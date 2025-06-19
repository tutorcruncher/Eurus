from sqlmodel import Session, select
from app.ai_tool.output_formats import SummaryOutput
from app.models.transcript import Feedback, Space, Summary, Transcript, UserSpaceModel


def create_transcript(
    db: Session, lesson_id: str, transcription: list[dict]
) -> Transcript:
    transcript = Transcript(lesson_id=lesson_id, transcription=transcription)
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript


def create_summary(db: Session, lesson_id: str, summary: SummaryOutput) -> Summary:
    summary = Summary(lesson_id=lesson_id, **summary.model_dump())
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


def create_feedback(
    db: Session,
    lesson_id: str,
    user_id: int,
    role: str,
    strengths: str,
    improvements: str,
) -> Feedback:
    feedback = Feedback(
        lesson_id=lesson_id,
        user_id=user_id,
        role=role,
        strengths=strengths,
        improvements=improvements,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_transcript(lesson_id: str, db: Session) -> Transcript | None:
    statement = select(Transcript).where(Transcript.lesson_id == lesson_id)
    return db.exec(statement).first()


def get_summary(lesson_id: str, db: Session) -> Summary | None:
    """Retrieve ``Summary`` for a given ``lesson_id``.

    A ``Summary`` is linked to a ``Transcript`` via ``transcript_id`` so we
    first find the transcript and then the related summary.
    """
    statement = select(Summary).where(Summary.lesson_id == lesson_id)
    return db.exec(statement).first()


def get_feedback(lesson_id: str, db: Session) -> list[Feedback]:
    statement = select(Feedback).where(Feedback.lesson_id == lesson_id)
    return db.exec(statement).all()


def get_or_create_space(db: Session, lesson_id: str, lesson_space_id: str) -> Space:
    statement = (
        select(Space)
        .where(Space.lesson_space_id == lesson_space_id)
        .where(Space.lesson_id == lesson_id)
    )
    space = db.exec(statement).first()
    if not space:
        space = Space(lesson_id=lesson_id, lesson_space_id=lesson_space_id)
        db.add(space)
        db.commit()
        db.refresh(space)
    return space


def create_or_update_user_space(
    db: Session, user_id: int, lesson_id: str, role: str, leader: bool
) -> UserSpaceModel:
    statement = (
        select(UserSpaceModel)
        .where(UserSpaceModel.user_id == user_id)
        .where(UserSpaceModel.lesson_id == lesson_id)
    )
    user_space = db.exec(statement).first()
    if user_space:
        user_space.role = role
        user_space.leader = leader
    else:
        user_space = UserSpaceModel(
            user_id=user_id, space_id=space_id, role=role, leader=leader
        )
        db.add(user_space)
    db.commit()
    db.refresh(user_space)
    return user_space


def get_user_spaces(lesson_id: str, db: Session) -> list[UserSpaceModel]:
    statement = select(UserSpaceModel).where(UserSpaceModel.lesson_id == lesson_id)
    return db.exec(statement).all()
