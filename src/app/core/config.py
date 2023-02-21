from datetime import datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

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

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
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

    ASYNC_DB_URI: Optional[str]

    @validator("ASYNC_DB_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
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
    result_backend: str

    WS_MESSAGE_QUEUE: str

    # --------------------------------------------------
    # > Mail
    # --------------------------------------------------
    MAIL_USERNAME: Optional[str]
    MAIL_PASSWORD: Optional[str]
    MAIL_FROM: Optional[str]
    MAIL_PORT: Optional[int]
    MAIL_SERVER: Optional[str]
    MAIL_STARTTLS: Optional[bool]
    MAIL_SSL_TLS: Optional[bool]
    EMAIL_TEMPLATES_DIR: Optional[Path | str] = Path(__file__).parent.parent / "templates/"
    EMAIL_CONNECTION_CONFIG: Optional[ConnectionConfig] = None

    @validator("EMAIL_CONNECTION_CONFIG", pre=True)
    def assemble_email_config(
        cls, v: Optional[ConnectionConfig], values: Dict[str, Any]
    ) -> Optional[ConnectionConfig]:
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
    BACKEND_CORS_ORIGINS: List[str] | List[AnyHttpUrl]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
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
    def assemble_log_rotation(cls, v: Optional[str]) -> time:
        if isinstance(v, str):
            return datetime.strptime(v, "%H:%M").time()
        else:
            return datetime.strptime("00:00", "%H:%M").time()

    @validator("LOG_RETENTION", pre=True)
    def assemble_log_retention(cls, v: Optional[int]) -> timedelta:
        if isinstance(v, int):
            return timedelta(days=v)
        else:
            return timedelta(days=3)

    class Config:
        case_sensitive = True
        # env_file = os.path.expanduser("~/.env")


@lru_cache()
def get_settings() -> BaseSettings:
    logger.info("Loading config settings from the environment...")
    return Settings()


@lru_cache()
def load_log_config():
    log_settings = LogSettings()
    logging.setup(
        log_settings.LOG_FILE_NAME,
        log_settings.LOG_ROTATION,
        log_settings.LOG_RETENTION,
    )


settings = get_settings()
