from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.testclient import TestClient

from app.middleware import api_key_auth_middleware
from app.utils.settings import get_settings


def _create_test_app() -> FastAPI:
    app = FastAPI()
    app.middleware('http')(api_key_auth_middleware)

    @app.get('/api/endpoint')
    def protected():
        return PlainTextResponse('protected')

    @app.get('/api/space/webhook/transcription/{lesson_id}')
    def transcription_webhook(lesson_id: str):
        return PlainTextResponse(f'webhook-{lesson_id}')

    @app.get('/public')
    def public():
        return PlainTextResponse('public')

    return app


def test_api_key_middleware(monkeypatch):
    """Ensure the middleware correctly enforces and bypasses API-key checks."""

    settings = get_settings()
    app = _create_test_app()
    client = TestClient(app)

    # 1. A request to an /api/ path without a key should be rejected.
    response = client.get('/api/endpoint')
    assert response.status_code == 401
    assert 'Invalid or missing API key' in response.text

    # 2. Providing the correct key passes the middleware.
    response = client.get('/api/endpoint', headers={'X-API-Key': settings.api_key})
    assert response.status_code == 200
    assert response.text == 'protected'

    # 3. Routes outside the /api/ prefix are not protected.
    response = client.get('/public')
    assert response.status_code == 200
    assert response.text == 'public'

    # 4. The transcription webhook path should bypass the key requirement.
    response = client.get('/api/space/webhook/transcription/123')
    assert response.status_code == 200
    assert response.text == 'webhook-123'
