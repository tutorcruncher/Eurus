# Add new test file covering all space API routes
import datetime
import pytest
from fastapi.testclient import TestClient
import importlib

from app.main import app
from app.utils.settings import get_settings
from app.schema.space import SpaceResponse, UserSpace
from app.schema.transcript import TranscriptResponse

from app.api import space as space_module
from app.services.lessonspace import LessonspaceService
from app.services.transcription import TranscriptionService
from app.services.lesson_planning import LessonPlanService, LessonSequenceService
from app.db.session import get_db


# ---------------------------------------------------------------------------
# Dependency stubs
# ---------------------------------------------------------------------------


class _DummyLessonspaceService:
    """Stub that mimics LessonspaceService.get_or_create_space."""

    async def get_or_create_space(self, request, db):  # type: ignore[override]
        # Return a predictable SpaceResponse so tests can assert on it.
        return SpaceResponse(
            space_id='space-001',
            lesson_id=request.lesson_id,
            tutor_spaces=[
                UserSpace(
                    user_id=request.tutors[0].user_id,
                    name=request.tutors[0].name,
                    role='tutor',
                    space_url='https://lesson.space/tutor/1',
                    leader=True,
                )
            ],
            student_spaces=[
                UserSpace(
                    user_id=request.students[0].user_id,
                    name=request.students[0].name,
                    role='student',
                    space_url='https://lesson.space/student/1',
                    leader=False,
                )
            ],
        )


class _DummyTranscriptionService:
    """Stub for every async method used in the space API routes."""

    def __init__(self):
        self.handled = False
        self.handled_lesson_id = None
        self.handled_webhook = None

    async def handle_webhook(self, webhook, lesson_id, db):  # type: ignore[override]
        # Simply record the call – business logic is irrelevant for route tests.
        self.handled = True
        self.handled_lesson_id = lesson_id
        self.handled_webhook = webhook

    async def get_transcript_by_id(self, lesson_id, db):  # type: ignore[override]
        # Return a minimal TranscriptResponse payload.
        return {
            'id': 1,
            'lesson_id': lesson_id,
            'transcription': {
                'transcription': [
                    {
                        'start_time': 0.0,
                        'end_time': 1.0,
                        'user': {'id': 1, 'name': 'User1'},
                        'breakout_id': 'main',
                        'text': 'Hello',
                    }
                ]
            },
            'created_at': '2020-01-01T00:00:00',
            'updated_at': '2020-01-01T00:00:00',
        }

    async def get_lesson_summary(self, lesson_id, db):  # type: ignore[override]
        return {
            'transcription': [],
            'feedback': [],
            'chapters': [],
            'key_points': 'Highlights',
            'short_summary': 'Short',
            'long_summary': 'Long',
            'recommended_focus': 'Focus',
        }


class _DummyLessonPlanService:
    async def create_lesson_plan(self, info):  # type: ignore[override]
        return 'Here is a lesson plan'


class _DummyLessonSequenceService:
    async def create_lesson_sequence(self, info):  # type: ignore[override]
        return {
            'lesson_plans': [
                {'lesson_plan': 'Plan 1'},
                {'lesson_plan': 'Plan 2'},
            ]
        }


# ---------------------------------------------------------------------------
# Pytest fixtures wiring the stubs into FastAPI dependency system.
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _override_dependencies():
    """Automatically apply dependency overrides for every test in this module."""

    dummy_lessonspace = _DummyLessonspaceService()
    dummy_transcription = _DummyTranscriptionService()
    dummy_lesson_plan = _DummyLessonPlanService()
    dummy_lesson_sequence = _DummyLessonSequenceService()

    app.dependency_overrides[LessonspaceService] = lambda: dummy_lessonspace
    app.dependency_overrides[TranscriptionService] = lambda: dummy_transcription
    app.dependency_overrides[LessonPlanService] = lambda: dummy_lesson_plan
    app.dependency_overrides[LessonSequenceService] = lambda: dummy_lesson_sequence
    app.dependency_overrides[get_db] = lambda: None

    # Patch the TranscriptionService reference inside the space router module so that
    # direct instantiation within the route (service = TranscriptionService()) returns
    # our stubbed instance instead of hitting real logic.
    space_mod = importlib.import_module('app.api.space')
    space_mod.TranscriptionService = lambda: dummy_transcription

    yield  # run the test

    # Clean-up after each test so other test modules are not affected.
    app.dependency_overrides.clear()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

_settings = get_settings()
_AUTH_HEADER = {'X-API-Key': _settings.api_key}


def _sample_space_request_json():
    return {
        'lesson_id': 'lesson-123',
        'tutors': [
            {
                'user_id': 1,
                'name': 'Tutor',
                'email': 'tutor@example.com',
                'is_leader': True,
            }
        ],
        'students': [
            {
                'user_id': 2,
                'name': 'Student',
                'email': 'student@example.com',
            }
        ],
        # Provide a fixed datetime to avoid serialization surprises
        'not_before': datetime.datetime(2020, 1, 1, 12, 0, 0).isoformat(),
    }


# ---------------------------------------------------------------------------
# Tests – one per route to ensure we execute every code-path in app/api/space.py
# ---------------------------------------------------------------------------


def test_create_space_route(client):
    """POST /api/space/ should return a fully-formed SpaceResponse."""
    response = client.post(
        '/api/space/', json=_sample_space_request_json(), headers=_AUTH_HEADER
    )
    assert response.status_code == 200
    data = response.json()

    assert data['lesson_id'] == 'lesson-123'
    assert data['space_id'] == 'space-001'
    # Ensure the payload contains tutor & student spaces as lists.
    assert len(data['tutor_spaces']) == 1
    assert len(data['student_spaces']) == 1


def test_transcription_webhook_route(client):
    """POST /api/space/webhook/transcription/{lesson_id} should delegate to the service and return success."""
    payload = {'transcriptionUrl': 'https://example.com/lesson.json'}
    response = client.post(
        '/api/space/webhook/transcription/lesson-123',
        json=payload,
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'success'}


def test_get_transcript_route(client):
    """GET /api/space/transcripts/{lesson_id} returns TranscriptResponse shaped data."""
    response = client.get('/api/space/transcripts/lesson-123', headers=_AUTH_HEADER)
    assert response.status_code == 200

    data = response.json()
    assert data['lesson_id'] == 'lesson-123'
    assert 'transcription' in data


def test_get_lesson_summary_route(client):
    """GET /api/space/lesson-summary/{lesson_id} returns merged lesson summary information."""
    response = client.get('/api/space/lesson-summary/lesson-123', headers=_AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()

    # Basic shape checks – each key should exist with our stubbed values
    assert data['key_points'] == 'Highlights'
    assert data['short_summary'] == 'Short'
    assert data['long_summary'] == 'Long'
    assert data['recommended_focus'] == 'Focus'
    assert data['chapters'] == []


def test_create_lesson_plan_route(client):
    """POST /api/space/create-lesson-plan constructs the LessonPlanResponse wrapper."""
    payload = {'topic': 'math'}
    response = client.post(
        '/api/space/create-lesson-plan', json=payload, headers=_AUTH_HEADER
    )
    assert response.status_code == 200
    assert response.json() == {'lesson_plan': 'Here is a lesson plan'}


def test_create_lesson_sequence_route(client):
    """POST /api/space/create-lesson-sequence returns the raw service payload."""
    payload = {'topic': 'science'}
    response = client.post(
        '/api/space/create-lesson-sequence', json=payload, headers=_AUTH_HEADER
    )
    assert response.status_code == 200
    assert response.json() == {
        'lesson_plans': [
            {'lesson_plan': 'Plan 1'},
            {'lesson_plan': 'Plan 2'},
        ]
    }
