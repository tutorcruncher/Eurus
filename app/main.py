import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import logfire
from app.api.core import router
from app.core.config import get_settings
from app.middleware import api_key_auth_middleware

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn)


def scrub_sensitive_data(record):
    # Remove sensitive data from logs
    if "headers" in record:
        if "Authorization" in record["headers"]:
            record["headers"]["Authorization"] = "***REDACTED***"
    return record


logfire.configure(
    service_name="janus",
    scrubbing=logfire.ScrubbingOptions(callback=scrub_sensitive_data),
)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.middleware("http")(api_key_auth_middleware)

logfire.instrument_fastapi(app)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
