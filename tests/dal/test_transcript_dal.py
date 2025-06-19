from sqlmodel import SQLModel, Session, create_engine

from app.dal import transcript as dal
from app.ai_tool.output_formats import SummaryOutput


# NB:  The project targets PostgreSQL in production, therefore we run the tests
# against a real PostgreSQL instance as well.  The helper below now initialises
# a Session bound to the database specified via the ``TEST_DATABASE_URL``
# environment variable.  If that variable is not provided we fall back to a
# reasonable local default.  Using PostgreSQL avoids incompatibilities (e.g.
# JSONB column types) that arise when using an in-memory SQLite database.


def _memory_session():
    """Return a `Session` bound to the (temporary) Postgres test database.

    The caller is still responsible for using the returned Session as a context
    manager (``with _memory_session() as s: ...``).  All tables are created on
    the fly so the database can be reused across test runs without manual
    migration steps.
    """

    import os

    db_url = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/eurus_test',
    )

    engine = create_engine(db_url, echo=False)

    # Tear-down any leftover state from a previous test run so each test starts
    # from a pristine schema.  Silence errors if the tables haven't been
    # created yet.
    SQLModel.metadata.drop_all(engine)  # type: ignore[arg-type]
    SQLModel.metadata.create_all(engine)

    return Session(engine)


def test_full_transcript_dal_cycle():
    """Exercise the full DAL workflow for transcripts, summaries, feedback and spaces."""

    lesson_id = 'lesson-dal-123'
    transcription_data = [
        {
            'start_time': 0.0,
            'end_time': 1.0,
            'user': {'id': 1, 'name': 'Tutor'},
            'breakout_id': 'main',
            'text': 'Welcome to the class!',
        }
    ]

    with _memory_session() as session:
        # 1. Transcript CRUD
        transcript_obj = dal.create_transcript(session, lesson_id, transcription_data)
        assert transcript_obj.id is not None

        fetched_transcript = dal.get_transcript(lesson_id, session)
        assert fetched_transcript is not None
        assert fetched_transcript.id == transcript_obj.id

        # 2. Summary CRUD
        summary_payload = SummaryOutput(
            key_points='Key points',
            short_summary='s' * 60,
            long_summary='l' * 1200,
            recommended_focus='r' * 60,
        )
        summary_obj = dal.create_summary(session, lesson_id, summary_payload)
        assert summary_obj.id is not None

        fetched_summary = dal.get_summary(lesson_id, session)
        assert fetched_summary is not None
        assert fetched_summary.id == summary_obj.id

        # 3. Feedback CRUD
        feedback_obj = dal.create_feedback(
            session,
            lesson_id=lesson_id,
            user_id=1,
            role='tutor',
            strengths='Great explanation',
            improvements='Speak slower',
        )
        assert feedback_obj.id is not None

        feedback_list = dal.get_feedback(lesson_id, session)
        assert len(feedback_list) == 1
        assert feedback_list[0].id == feedback_obj.id

        # 4. Space + UserSpace CRUD
        space_obj = dal.get_or_create_space(session, lesson_id, 'space-xyz')
        assert space_obj.id is not None
        # Calling again should *not* create a duplicate.
        same_space_obj = dal.get_or_create_space(session, lesson_id, 'space-xyz')
        assert same_space_obj.id == space_obj.id

        user_space_obj = dal.create_or_update_user_space(
            session, user_id=9, lesson_id=lesson_id, role='student', leader=False
        )
        assert user_space_obj.leader is False

        # Update leader flag – should update instead of creating a new row.
        user_space_updated = dal.create_or_update_user_space(
            session, user_id=9, lesson_id=lesson_id, role='student', leader=True
        )
        assert user_space_updated.id == user_space_obj.id
        assert user_space_updated.leader is True
