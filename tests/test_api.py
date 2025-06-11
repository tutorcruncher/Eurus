import pytest
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
    async def mock_post(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass
            
            def json(self):
                return {
                    'url': 'https://lessonspace.com/space/123',
                    'id': '123',
                }
        return MockResponse()
    
    monkeypatch.setattr('httpx.AsyncClient.post', mock_post)
    
    # Mock Redis setex
    monkeypatch.setattr('app.services.lessonspace.redis_client.setex', lambda *args: None)
    
    response = client.post(
        '/api/v1/spaces',
        json={
            'lesson_id': 'test-lesson',
            'teacher_name': 'Test Teacher',
            'student_name': 'Test Student',
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['space_url'] == 'https://lessonspace.com/space/123'
    assert data['space_id'] == '123'
    assert data['lesson_id'] == 'test-lesson' 