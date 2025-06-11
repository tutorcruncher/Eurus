import pytest
import json
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
                if "/v2/spaces/launch/" in url:
                    return {
                        "client_url": "https://go.room.sh/test-space",
                        "room_id": "test-room-id",
                        "session_id": "test-session-id",
                        "user_id": "test-user-id",
                    }

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    # Mock Redis setex
    monkeypatch.setattr(
        "app.services.lessonspace.redis_client.setex", lambda *args: None
    )

    response = client.post(
        "/api/space",
        json={
            "lesson_id": "test-lesson",
            "tutors": [
                {
                    "name": "Test Tutor 1",
                    "email": "tutor1@example.com",
                    "is_leader": True
                },
                {
                    "name": "Test Tutor 2",
                    "email": "tutor2@example.com",
                    "is_leader": False
                },
            ],
            "students": [
                {"name": "Test Student 1", "email": "student1@example.com"},
                {"name": "Test Student 2", "email": "student2@example.com"},
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["space_id"] == "test-room-id"
    assert data["lesson_id"] == "test-lesson"
    assert len(data["tutor_spaces"]) == 2
    assert len(data["student_spaces"]) == 2
    
    # Verify tutor spaces
    tutor1 = next(t for t in data["tutor_spaces"] if t["email"] == "tutor1@example.com")
    assert tutor1["name"] == "Test Tutor 1"
    assert tutor1["role"] == "tutor"
    assert tutor1["space_url"] == "https://go.room.sh/test-space"

    # Verify student spaces
    student1 = next(s for s in data["student_spaces"] if s["email"] == "student1@example.com")
    assert student1["name"] == "Test Student 1"
    assert student1["role"] == "student"
    assert student1["space_url"] == "https://go.room.sh/test-space"


def test_get_existing_space(client, monkeypatch):
    # Mock Redis get to return cached space
    cached_space = {
        "space_id": "existing-room-id",
        "lesson_id": "test-lesson",
        "tutor_spaces": [
            {
                "email": "tutor1@example.com",
                "name": "Test Tutor 1",
                "role": "tutor",
                "space_url": "https://go.room.sh/existing-space"
            }
        ],
        "student_spaces": [
            {
                "email": "student1@example.com",
                "name": "Test Student 1",
                "role": "student",
                "space_url": "https://go.room.sh/existing-space"
            }
        ]
    }
    monkeypatch.setattr(
        "app.services.lessonspace.redis_client.get", lambda x: json.dumps(cached_space)
    )

    response = client.post(
        "/api/space",
        json={
            "lesson_id": "test-lesson",
            "tutors": [
                {
                    "name": "Test Tutor 1",
                    "email": "tutor1@example.com",
                    "is_leader": True
                }
            ],
            "students": [
                {"name": "Test Student 1", "email": "student1@example.com"}
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["space_id"] == "existing-room-id"
    assert data["lesson_id"] == "test-lesson"
    assert len(data["tutor_spaces"]) == 1
    assert len(data["student_spaces"]) == 1
    assert data["tutor_spaces"][0]["space_url"] == "https://go.room.sh/existing-space"
    assert data["student_spaces"][0]["space_url"] == "https://go.room.sh/existing-space"
