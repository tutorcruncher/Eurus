import sentry_sdk
from fastapi import FastAPI
import logfire
from app.utils.settings import get_settings
from app.middleware import api_key_auth_middleware
from app.schema.space import TranscriptionWebhook
from app.services.transcription import TranscriptionService
from app.api.space import router
from app.middleware import api_key_auth_middleware

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn)


def scrub_sensitive_data(record):
    if hasattr(record, 'value'):
        if isinstance(record.value, dict) and 'headers' in record.value:
            if 'Authorization' in record.value['headers']:
                record.value['headers']['Authorization'] = '***REDACTED***'
    elif isinstance(record, dict) and 'headers' in record:
        if 'Authorization' in record['headers']:
            record['headers']['Authorization'] = '***REDACTED***'
    return record


app = FastAPI(
    title=settings.app_name,
    debug=settings.dev,
)

app.middleware('http')(api_key_auth_middleware)

logfire.instrument_fastapi(app)

app.include_router(router)


@app.get('/health')
async def health_check():
    return {'status': 'healthy'}
