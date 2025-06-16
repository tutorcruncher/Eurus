from fastapi import Request, status
from fastapi.responses import JSONResponse
from settings import get_settings

settings = get_settings()


async def api_key_auth_middleware(request: Request, call_next):
    # Skip API key check for transcription webhook endpoint
    if request.url.path.startswith('/api/space/webhook/transcription/'):
        return await call_next(request)

    if request.url.path.startswith('/api/'):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != settings.api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Invalid or missing API key'},
            )
    return await call_next(request)
