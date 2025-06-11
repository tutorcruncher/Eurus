import pytest
import json
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'}


def test_create_space(client, monkeypatch):
    # Mock Redis get to return None (no cached space)
    monkeypatch.setattr('app.services.lessonspace.redis_client.get', lambda x: None)
    
    # Mock httpx.AsyncClient.post
    async def mock_post(self, url, *args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass
            
            def json(self):
                if '/v2/spaces/launch/' in url:
                    return {
                        'client_url': 'https://go.room.sh/test-space',
                        'room_id': 'test-room-id',
                        'session_id': 'test-session-id',
                        'user_id': 'test-user-id'
                    }
        return MockResponse()
    
    monkeypatch.setattr('httpx.AsyncClient.post', mock_post)
    
    # Mock Redis setex
    monkeypatch.setattr('app.services.lessonspace.redis_client.setex', lambda *args: None)
    
    response = client.post(
        '/api/v1/spaces',
        json={
            'lesson_id': 'test-lesson',
            'teachers': [
                {
                    'name': 'Test Teacher 1',
                    'email': 'teacher1@example.com'
                },
                {
                    'name': 'Test Teacher 2',
                    'email': 'teacher2@example.com'
                }
            ],
            'students': [
                {
                    'name': 'Test Student 1',
                    'email': 'student1@example.com'
                },
                {
                    'name': 'Test Student 2',
                    'email': 'student2@example.com'
                }
            ]
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['space_url'] == 'https://go.room.sh/test-space'
    assert data['space_id'] == 'test-room-id'
    assert data['lesson_id'] == 'test-lesson'


def test_get_existing_space(client, monkeypatch):
    # Mock Redis get to return cached space
    cached_space = {
        'space_url': 'https://go.room.sh/existing-space',
        'space_id': 'existing-room-id',
        'lesson_id': 'test-lesson'
    }
    monkeypatch.setattr(
        'app.services.lessonspace.redis_client.get',
        lambda x: json.dumps(cached_space)
    )
    
    response = client.post(
        '/api/v1/spaces',
        json={
            'lesson_id': 'test-lesson',
            'teachers': [
                {
                    'name': 'Test Teacher 1',
                    'email': 'teacher1@example.com'
                }
            ],
            'students': [
                {
                    'name': 'Test Student 1',
                    'email': 'student1@example.com'
                }
            ]
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['space_url'] == 'https://go.room.sh/existing-space'
    assert data['space_id'] == 'existing-room-id'
    assert data['lesson_id'] == 'test-lesson'
