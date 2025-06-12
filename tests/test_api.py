import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from httpx import HTTPStatusError
from datetime import datetime, timedelta


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_space(client, monkeypatch):
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
    response = client.post(
        "/api/space",
        json={
            "lesson_id": "test-lesson",
            "tutors": [
                {
                    "name": "Test Tutor 1",
                    "email": "tutor1@example.com",
                    "is_leader": True,
                },
                {
                    "name": "Test Tutor 2",
                    "email": "tutor2@example.com",
                    "is_leader": False,
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
    tutor1 = next(t for t in data["tutor_spaces"] if t["email"] == "tutor1@example.com")
    assert tutor1["name"] == "Test Tutor 1"
    assert tutor1["role"] == "tutor"
    assert tutor1["space_url"] == "https://go.room.sh/test-space"
    student1 = next(
        s for s in data["student_spaces"] if s["email"] == "student1@example.com"
    )
    assert student1["name"] == "Test Student 1"
    assert student1["role"] == "student"
    assert student1["space_url"] == "https://go.room.sh/test-space"


def test_create_space_no_tutors(client, monkeypatch):
    async def mock_post(self, url, *args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "client_url": "https://go.room.sh/test-space",
                    "room_id": "test-room-id",
                }

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    response = client.post(
        "/api/space",
        json={
            "lesson_id": "no-tutors-lesson",
            "tutors": [],
            "students": [{"name": "Student", "email": "student@example.com"}],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tutor_spaces"]) == 0
    assert len(data["student_spaces"]) == 1


def test_create_space_no_students(client, monkeypatch):
    async def mock_post(self, url, *args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "client_url": "https://go.room.sh/test-space",
                    "room_id": "test-room-id",
                }

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    response = client.post(
        "/api/space",
        json={
            "lesson_id": "no-students-lesson",
            "tutors": [
                {"name": "Tutor", "email": "tutor@example.com", "is_leader": True}
            ],
            "students": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tutor_spaces"]) == 1
    assert len(data["student_spaces"]) == 0


def test_create_space_duplicate_emails(client, monkeypatch):
    async def mock_post(self, url, *args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "client_url": "https://go.room.sh/test-space",
                    "room_id": "test-room-id",
                }

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    response = client.post(
        "/api/space",
        json={
            "lesson_id": "dup-email-lesson",
            "tutors": [
                {"name": "Tutor", "email": "dup@example.com", "is_leader": True}
            ],
            "students": [{"name": "Student", "email": "dup@example.com"}],
        },
    )
    assert response.status_code == 200
    data = response.json()
    # Both tutor and student with same email should be present
    assert len(data["tutor_spaces"]) == 1
    assert len(data["student_spaces"]) == 1
    assert data["tutor_spaces"][0]["email"] == "dup@example.com"
    assert data["student_spaces"][0]["email"] == "dup@example.com"


def test_create_space_invalid_email(client, monkeypatch):
    async def mock_post(self, url, *args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "client_url": "https://go.room.sh/test-space",
                    "room_id": "test-room-id",
                }

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    response = client.post(
        "/api/space",
        json={
            "lesson_id": "invalid-email-lesson",
            "tutors": [{"name": "Tutor", "email": "not-an-email", "is_leader": True}],
            "students": [],
        },
    )
    assert response.status_code == 422  # FastAPI should reject invalid email


def test_create_space_external_api_error(client, monkeypatch):
    async def mock_post(self, url, *args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                raise HTTPStatusError("error", request=None, response=None)

            def json(self):
                return {}

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    response = client.post(
        "/api/space",
        json={
            "lesson_id": "api-error-lesson",
            "tutors": [
                {"name": "Tutor", "email": "tutor@example.com", "is_leader": True}
            ],
            "students": [],
        },
    )
    assert response.status_code == 500


def test_create_space_malformed_json(client, monkeypatch):
    async def mock_post(self, url, *args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                raise ValueError("Malformed JSON")

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    response = client.post(
        "/api/space",
        json={
            "lesson_id": "malformed-json-lesson",
            "tutors": [
                {"name": "Tutor", "email": "tutor@example.com", "is_leader": True}
            ],
            "students": [],
        },
    )
    assert response.status_code == 500


def test_create_space_multiple_tutors_one_leader(client, monkeypatch):
    async def mock_post(self, url, *args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "client_url": "https://go.room.sh/test-space",
                    "room_id": "test-room-id",
                }

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    response = client.post(
        "/api/space",
        json={
            "lesson_id": "multi-leader-lesson",
            "tutors": [
                {"name": "Tutor1", "email": "t1@example.com", "is_leader": True},
                {"name": "Tutor2", "email": "t2@example.com", "is_leader": False},
            ],
            "students": [],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tutor_spaces"]) == 2
    assert any(
        t["role"] == "tutor" and t["email"] == "t1@example.com"
        for t in data["tutor_spaces"]
    )
    assert any(
        t["role"] == "tutor" and t["email"] == "t2@example.com"
        for t in data["tutor_spaces"]
    )


def test_create_space_parallel_many_users(client, monkeypatch):
    call_count = {"count": 0}

    async def mock_post(self, url, *args, **kwargs):
        call_count["count"] += 1

        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "client_url": f"https://go.room.sh/test-space/{call_count['count']}",
                    "room_id": "test-room-id",
                }

        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    tutors = [
        {"name": f"Tutor{i}", "email": f"tutor{i}@example.com", "is_leader": i == 0}
        for i in range(10)
    ]
    students = [
        {"name": f"Student{i}", "email": f"student{i}@example.com"} for i in range(20)
    ]
    response = client.post(
        "/api/space",
        json={
            "lesson_id": "parallel-many-users-lesson",
            "tutors": tutors,
            "students": students,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["tutor_spaces"]) == 10
    assert len(data["student_spaces"]) == 20


def test_create_space_with_not_before(client, monkeypatch):
    called = {}
    async def mock_post(self, url, *args, **kwargs):
        called['json'] = kwargs['json']
        class MockResponse:
            def raise_for_status(self):
                pass
            def json(self):
                return {"client_url": "https://lessonspace.com/join/abc", "room_id": "abc"}
        return MockResponse()
    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    not_before = (datetime.now() + timedelta(hours=1)).replace(microsecond=0)
    req = {
        "lesson_id": "lesson-x",
        "tutors": [{"name": "Tutor", "email": "tutor@x.com", "is_leader": True}],
        "students": [{"name": "Student", "email": "student@x.com"}],
        "not_before": not_before.isoformat()
    }
    resp = client.post("/api/space", json=req)
    assert resp.status_code == 200
    # Check that timeouts.not_before is present and correct
    assert 'timeouts' in called['json']
    assert called['json']['timeouts']['not_before'].startswith(not_before.isoformat()[:16])


def test_create_space_without_not_before(client, monkeypatch):
    called = {}
    async def mock_post(self, url, *args, **kwargs):
        called['json'] = kwargs['json']
        class MockResponse:
            def raise_for_status(self):
                pass
            def json(self):
                return {"client_url": "https://lessonspace.com/join/abc", "room_id": "abc"}
        return MockResponse()
    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    req = {
        "lesson_id": "lesson-y",
        "tutors": [{"name": "Tutor", "email": "tutor@y.com", "is_leader": True}],
        "students": [{"name": "Student", "email": "student@y.com"}]
    }
    resp = client.post("/api/space", json=req)
    assert resp.status_code == 200
    # Check that timeouts is not present
    assert 'timeouts' not in called['json']
