from functools import lru_cache
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    app_name: str = Field('Lessonspace Service', alias='APP_NAME')
    debug: bool = Field(False, alias='DEBUG')

    # Database settings
    database_url: str = Field(
        'postgresql://postgres:waffle@localhost:5432/eurus', alias='DATABASE_URL'
    )

    # Redis settings
    redis_url: str = Field('redis://localhost:6379/0", alias="REDIS_URL')

    # Lessonspace settings
    lessonspace_api_key: str = Field(..., alias='LESSONSPACE_API_KEY')
    lessonspace_api_url: str = Field(
        'https://api.thelessonspace.com/v2', alias='LESSONSPACE_API_URL'
    )

    # Sentry settings
    sentry_dsn: str | None = Field(None, alias='SENTRY_DSN')

    # API key for authentication
    api_key: str = Field(..., alias='API_KEY')

    # Base URL for webhooks
    webhook_base_url: str = Field(..., alias='WEBHOOK_BASE_URL')

    model_config = ConfigDict(
        extra='allow',
        env_file='.env',
        case_sensitive=True,
        env_prefix='',
        populate_by_name=True,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
