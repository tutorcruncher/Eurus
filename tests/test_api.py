import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_space(client, monkeypatch):
    # Mock Redis get to return None (no cached space)
    monkeypatch.setattr("app.services.lessonspace.redis_client.get", lambda x: None)

    # Mock httpx.AsyncClient.post
    async def mock_post(self, url, *args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                if "/spaces/" in url:
                    return {"status": "success"}
                return {
                    "url": "https://lessonspace.com/space/123",
                    "id": "123",
                }

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    # Mock Redis setex
    monkeypatch.setattr(
        "app.services.lessonspace.redis_client.setex", lambda *args: None
    )

    response = client.post(
        "/api/v1/spaces",
        json={
            "lesson_id": "test-lesson",
            "teachers": [
                {"name": "Test Teacher 1", "email": "teacher1@example.com"},
                {"name": "Test Teacher 2", "email": "teacher2@example.com"},
            ],
            "students": [
                {"name": "Test Student 1", "email": "student1@example.com"},
                {"name": "Test Student 2", "email": "student2@example.com"},
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["space_url"] == "https://lessonspace.com/space/123"
    assert data["space_id"] == "123"
    assert data["lesson_id"] == "test-lesson"
