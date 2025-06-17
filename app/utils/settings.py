from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict, Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    app_name: str = Field('Lessonspace Service', alias='APP_NAME')
    dev: bool = Field(False, alias='DEV')
    database_url: str = Field(
        'postgresql://postgres:waffle@localhost:5432/eurus', alias='DATABASE_URL'
    )
    redis_url: str = Field('redis://localhost:6379/0", alias="REDIS_URL')
    lessonspace_api_key: str = Field(..., alias='LESSONSPACE_API_KEY')
    lessonspace_api_url: str = Field(
        'https://api.thelessonspace.com/v2', alias='LESSONSPACE_API_URL'
    )
    sentry_dsn: str | None = Field(None, alias='SENTRY_DSN')
    api_key: str = Field(default='test-key', alias='API_KEY')
    base_url: str = Field(default='http://localhost:8000', alias='BASE_URL')
    model_config = ConfigDict(
        extra='allow',
        env_file='.env',
        case_sensitive=True,
        env_prefix='',
        populate_by_name=True,
    )

    ai_model: str = Field(default='openai:gpt-4o', alias='AI_MODEL')
    openai_api_key: str = Field(default='', alias='OPENAI_API_KEY')
    model_config = SettingsConfigDict(env_file='.env', extra='allow')


@lru_cache()
def get_settings() -> Settings:
    return Settings()
