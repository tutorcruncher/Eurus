import sentry_sdk
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from app.db.session import engine
from app.utils.settings import get_settings
from app.middleware import api_key_auth_middleware
from app.api.space import router
import logfire

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup and dispose engine on shutdown."""
    # Create all tables if they do not exist yet.
    SQLModel.metadata.create_all(bind=engine)
    yield
    # Gracefully dispose the engine once the application stops.
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    debug=settings.dev,
    lifespan=lifespan,
)

app.middleware('http')(api_key_auth_middleware)

if settings.logfire_token:
    logfire.instrument_fastapi(app)
    logfire.instrument_pydantic_ai()


app.include_router(router)


@app.get('/')
async def health_check():
    return {'status': 'healthy'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'app.main:app', host=settings.api_host, port=settings.api_port, reload=True
    )
