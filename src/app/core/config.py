from datetime import datetime, time, timedelta
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi_mail import ConnectionConfig
from loguru import logger
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core import logging


class ModeEnum(str, Enum):
    development = "development"
    production = "production"
    testing = "testing"


class Settings(BaseSettings):
    # --------------------------------------------------
    # > Application
    # --------------------------------------------------
    MODE: ModeEnum = ModeEnum.development

    APP_TITLE: str = "yuno"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "My app"

    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"

    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 90  # 90 days

    OTP_EXPIRE_MINUTES: int = 5  # 5 minutes
    RESET_TOKEN_EXPITE_MINUTES: int = 30  # 30 minutes

    # --------------------------------------------------
    # > Postgres
    # --------------------------------------------------
    DB_SCHEME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    ASYNC_DATABASE_URI: str | None

    @field_validator("ASYNC_DATABASE_URI", mode="after")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            if v == "":
                return PostgresDsn.build(
                    scheme=info.data["DB_SCHEME"],
                    user=info.data["DB_USER"],
                    password=info.data["DB_PASSWORD"],
                    host=info.data["DB_HOST"],
                    port=str(info.data["DB_PORT"]),
                    path=f"/{info.data['DB_NAME'] or ''}",
                )
        return v

    # --------------------------------------------------
    # > Minio
    # --------------------------------------------------
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_URL: str
    MINIO_BUCKET: str

    # --------------------------------------------------
    # > Redis
    # --------------------------------------------------
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str
    REDIS_POOL_SIZE: str

    # --------------------------------------------------
    # > Celery
    # --------------------------------------------------
    CELERY_BROKER_URL: str
    RESULT_BACKEND: str

    WS_MESSAGE_QUEUE: str

    # --------------------------------------------------
    # > Misc
    # --------------------------------------------------
    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl]

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(case_sensitive=True)


class MailConnectionConfig(BaseSettings):
    MAIL_USERNAME: str | None
    MAIL_PASSWORD: str | None
    MAIL_FROM: str | None
    MAIL_PORT: int | None
    MAIL_SERVER: str | None
    MAIL_STARTTLS: bool | None
    MAIL_SSL_TLS: bool | None
    EMAIL_TEMPLATES_DIR: Path | str | None = Path(__file__).parent.parent / "templates/"
    EMAIL_CONNECTION_CONFIG: ConnectionConfig | None = None

    model_config = SettingsConfigDict(case_sensitive=True)


class LogSettings(BaseSettings):
    LOG_FILE_NAME: str = "log_file_name.log"
    LOG_ROTATION: time
    LOG_RETENTION: timedelta

    @field_validator("LOG_ROTATION", mode="before")
    @classmethod
    def assemble_log_rotation(cls, v: str | None) -> time:
        if isinstance(v, str):
            return datetime.strptime(v, "%H:%M").time()
        else:
            return datetime.strptime("00:00", "%H:%M").time()

    @field_validator("LOG_RETENTION", mode="before")
    @classmethod
    def assemble_log_retention(cls, v: int | None) -> timedelta:
        if isinstance(v, int):
            return timedelta(days=v)
        else:
            return timedelta(days=3)

    model_config = SettingsConfigDict(case_sensitive=True)


@lru_cache
def get_settings() -> Settings:
    logger.info("Loading config settings from the environment...")
    return Settings()


@lru_cache
def load_log_config():
    log_settings = LogSettings()
    logging.setup(
        log_settings.LOG_FILE_NAME,
        log_settings.LOG_ROTATION,
        log_settings.LOG_RETENTION,
    )


settings = get_settings()
