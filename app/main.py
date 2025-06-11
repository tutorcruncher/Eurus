import sentry_sdk
from fastapi import FastAPI
import logfire
from app.api.core import router
from app.core.config import get_settings

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn)

logfire.configure()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

logfire.instrument_fastapi(app)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
