from datetime import datetime, timezone

from app.models.transcript import Transcript, UserSpaceModel


def _sample_transcript() -> Transcript:
    """Create an in-memory ``Transcript`` instance with two speakers."""
    return Transcript(
        lesson_id='lesson-xyz',
        transcription=[
            {
                'start_time': 0.0,
                'end_time': 1.0,
                'user': {'id': 3632572, 'name': 'Alice'},
                'breakout_id': 'main',
                'text': 'Hello there.',
            },
            {
                'start_time': 1.0,
                'end_time': 2.0,
                'user': {'id': 123, 'name': 'Bob'},
                'breakout_id': 'main',
                'text': 'Hi Alice!',
            },
            {
                'start_time': 2.0,
                'end_time': 3.0,
                'user': {'id': 3632572, 'name': 'Alice'},
                'breakout_id': 'main',
                'text': 'How are you?',
            },
        ],
        created_at=datetime.now(timezone.utc),
    )


def test_transcript_helper_methods():
    transcript = _sample_transcript()

    # 1. ``to_concatonated_transcript`` joins the text fields with newlines.
    concatenated = transcript.to_concatonated_transcript()
    assert 'Hello there.' in concatenated
    assert 'Hi Alice!' in concatenated
    # There should be exactly three newline characters joining two breaks.
    assert concatenated.count('\n') == 2

    # 2. ``get_user_transcript`` filters by ``user_id``.
    alice_text = transcript.get_user_transcript(3632572)
    assert 'Hello there.' in alice_text and 'How are you?' in alice_text
    # Bob's line must not be in Alice's transcript.
    assert 'Hi Alice!' not in alice_text

    # 3. ``gather_user_transcripts`` aggregates and labels by role.
    user_lookup = {
        3632572: UserSpaceModel(
            user_id=3632572, role='tutor', leader=True, lesson_id='lesson-xyz'
        ),
        123: UserSpaceModel(
            user_id=123, role='student', leader=False, lesson_id='lesson-xyz'
        ),
    }
    user_transcripts = transcript.gather_user_transcripts(user_lookup)

    # Two distinct users should be present.
    assert set(user_transcripts.keys()) == {3632572, 123}

    # The tutor (3632572) should have combined text from both of their segments.
    assert user_transcripts[3632572]['role'] == 'tutor'
    assert 'How are you?' in user_transcripts[3632572]['text']

    # The student (123) should be labelled as student and only have their own line.
    assert user_transcripts[123]['role'] == 'student'
    assert user_transcripts[123]['text'] == 'Hi Alice!'
