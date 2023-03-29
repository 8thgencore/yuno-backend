from datetime import datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi_mail import ConnectionConfig
from loguru import logger
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator

from app.core import logging


class Settings(BaseSettings):
    # --------------------------------------------------
    # > Application
    # --------------------------------------------------
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
    DB_PORT: int | str
    DB_NAME: str

    ASYNC_DB_URI: str | None

    @validator("ASYNC_DB_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme=values.get("DB_SCHEME"),
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=str(values.get("DB_PORT")),
            path=f"/{values.get('DB_NAME') or ''}",
        )

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
    # > Mail
    # --------------------------------------------------
    MAIL_USERNAME: str | None
    MAIL_PASSWORD: str | None
    MAIL_FROM: str | None
    MAIL_PORT: int | None
    MAIL_SERVER: str | None
    MAIL_STARTTLS: bool | None
    MAIL_SSL_TLS: bool | None
    EMAIL_TEMPLATES_DIR: Path | str | None = Path(__file__).parent.parent / "templates/"
    EMAIL_CONNECTION_CONFIG: ConnectionConfig | None = None

    @validator("EMAIL_CONNECTION_CONFIG", pre=True)
    def assemble_email_config(
        cls, v: ConnectionConfig | None, values: dict[str, Any]
    ) -> ConnectionConfig | None:
        if isinstance(v, ConnectionConfig):
            return v
        return ConnectionConfig(
            MAIL_USERNAME=values.get("MAIL_USERNAME"),
            MAIL_PASSWORD=values.get("MAIL_PASSWORD"),
            MAIL_FROM=values.get("MAIL_FROM"),
            MAIL_PORT=values.get("MAIL_PORT"),
            MAIL_SERVER=values.get("MAIL_SERVER"),
            MAIL_STARTTLS=values.get("MAIL_STARTTLS"),
            MAIL_SSL_TLS=values.get("MAIL_SSL_TLS"),
            TEMPLATE_FOLDER=values.get("EMAIL_TEMPLATES_DIR"),
        )

    # --------------------------------------------------
    # > Misc
    # --------------------------------------------------
    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        # env_file = os.path.expanduser("~/.env")


class LogSettings(BaseSettings):
    LOG_FILE_NAME: str = "log_file_name.log"
    LOG_ROTATION: time
    LOG_RETENTION: timedelta

    @validator("LOG_ROTATION", pre=True)
    def assemble_log_rotation(cls, v: str | None) -> time:
        if isinstance(v, str):
            return datetime.strptime(v, "%H:%M").time()
        else:
            return datetime.strptime("00:00", "%H:%M").time()

    @validator("LOG_RETENTION", pre=True)
    def assemble_log_retention(cls, v: int | None) -> timedelta:
        if isinstance(v, int):
            return timedelta(days=v)
        else:
            return timedelta(days=3)

    class Config:
        case_sensitive = True
        # env_file = os.path.expanduser("~/.env")


@lru_cache
def get_settings() -> BaseSettings:
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
