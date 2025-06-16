import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from app.models.space import (
    SpaceRequest,
    TranscriptionWebhook,
    LeaderUser,
    User,
    UserSpace,
)
from app.services.lessonspace import LessonspaceService
from datetime import datetime, timezone
import json


@pytest.fixture
def mock_space_request():
    return SpaceRequest(
        lesson_id='test-lesson-123',
        tutors=[
            LeaderUser(user_id='tutor-1', name='Tutor One', is_leader=True),
            LeaderUser(user_id='tutor-2', name='Tutor Two', is_leader=False),
        ],
        students=[
            User(user_id='student-1', name='Student One'),
            User(user_id='student-2', name='Student Two'),
        ],
        not_before=datetime(2024, 3, 20, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_space_response():
    return {
        'space_id': 'test-space-123',
        'lesson_id': 'test-lesson-123',
        'tutor_spaces': [
            {
                'user_id': 'tutor-1',
                'name': 'Tutor One',
                'role': 'tutor',
                'space_url': 'https://test.thelessonspace.com/space/tutor-1',
            }
        ],
        'student_spaces': [
            {
                'user_id': 'student-1',
                'name': 'Student One',
                'role': 'student',
                'space_url': 'https://test.thelessonspace.com/space/student-1',
            }
        ],
    }


@pytest.mark.asyncio
async def test_create_space_success(
    client, mock_space_request, mock_space_response, test_env_vars
):
    with patch.object(
        LessonspaceService, 'get_or_create_space', return_value=mock_space_response
    ):
        response = client.post(
            '/api/space/',
            data=mock_space_request.model_dump_json(),
            headers={'Content-Type': 'application/json', 'X-API-Key': 'test'},
        )
        assert response.status_code == 200
        assert response.json() == mock_space_response


@pytest.mark.asyncio
async def test_handle_transcription_webhook_success(client, db_session, test_env_vars):
    webhook_data = {'transcriptionUrl': 'http://test-url.com/transcript'}
    lesson_id = 'test-lesson-123'

    with patch(
        'app.services.transcription.TranscriptionService.handle_webhook'
    ) as mock_handle:
        mock_handle.return_value = None
        response = client.post(
            f'/api/space/webhook/transcription/{lesson_id}',
            json=webhook_data,
            headers={'X-API-Key': 'test'},
        )
        assert response.status_code == 200
        assert response.json() == {'status': 'success'}


@pytest.mark.asyncio
async def test_get_transcript_success(client, db_session, test_env_vars):
    from app.models.transcript import Transcript
    from datetime import datetime
    import json

    lesson_id = 'test-lesson-123'
    now = datetime.now(timezone.utc)
    zulu = now.replace(tzinfo=None).isoformat(timespec='microseconds') + 'Z'
    transcription_data = [
        {
            'start_time': 0.0,
            'end_time': 1.0,
            'user': {'id': 1, 'name': 'Alice'},
            'breakout_id': 'main',
            'text': 'Hello world.',
        }
    ]
    transcript = Transcript(
        lesson_id=lesson_id,
        transcription=transcription_data,
        created_at=now,
        updated_at=now,
    )
    db_session.add(transcript)
    db_session.commit()
    db_session.refresh(transcript)

    response = client.get(
        f'/api/space/transcripts/{lesson_id}', headers={'X-API-Key': 'test'}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['lesson_id'] == lesson_id
    assert data['transcription'][0]['text'] == 'Hello world.'


@pytest.mark.asyncio
async def test_get_transcript_not_found(client, db_session, test_env_vars):
    lesson_id = 'non-existent-lesson'
    response = client.get(
        f'/api/space/transcripts/{lesson_id}', headers={'X-API-Key': 'test'}
    )
    assert response.status_code == 404
    assert (
        'Transcript not found' in response.json().get('detail', '')
        or response.json().get('detail', '') == 'Not Found'
    )
