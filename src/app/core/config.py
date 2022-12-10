from dataclasses import dataclass, fields
from datetime import datetime, time, timedelta
from functools import lru_cache
from typing import List

from environs import Env

from app.core import logging


@dataclass
class Application:
    title: str
    version: str
    description: str
    cors_origins: List[str]


@dataclass
class DbConfig:
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DATABASE: str
    DATABASE_URI: str = ""

    def __post_init__(self) -> None:
        self.DATABASE_URI = f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"


@dataclass
class RedisConfig:
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str
    REDIS_POOL_SIZE: int


@dataclass
class LogConfig:
    file_name: str
    rotation: time
    retention: timedelta


@dataclass
class Authentication:
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str


@dataclass
class Miscellaneous:
    pass


@dataclass
class Config:
    app: Application
    db: DbConfig
    redis: RedisConfig
    log: LogConfig
    auth: Authentication
    misc: Miscellaneous


@lru_cache()
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        app=Application(
            title=env.str("APP_NAME"),
            version=env.str("APP_VERSION", "1.0.0"),
            description=env.str("APP_DESCRIPTION", "My app"),
            cors_origins=env.str("BACKEND_CORS_ORIGINS", "*"),
        ),
        db=DbConfig(
            USER=env.str("DB_USER"),
            PASSWORD=env.str("DB_PASS"),
            HOST=env.str("DB_HOST"),
            PORT=env.int("DB_PORT"),
            DATABASE=env.str("DB_NAME"),
        ),
        redis=RedisConfig(
            REDIS_HOST=env.str("REDIS_HOST"),
            REDIS_PASS=env.str("REDIS_PASS"),
            REDIS_PORT=env.int("REDIS_PORT"),
            REDIS_POOL_SIZE=env.int("REDIS_POOL_SIZE"),
        ),
        log=LogConfig(
            file_name=env.str("LOG_FILE_NAME"),
            rotation=datetime.strptime(env.str("LOG_ROTATION"), "%H:%M").time(),
            retention=timedelta(days=env.int("LOG_RETENTION")),
        ),
        auth=Authentication(
            ACCESS_TOKEN_EXPIRE_MINUTES=60 * 24 * 8,
            REFRESH_TOKEN_EXPIRE_MINUTES=60 * 24 * 180,
            SECRET_KEY="sdsdsd",
        ),
        misc=Miscellaneous(),
    )


@lru_cache()
def load_log_config():
    logging.setup(
        settings.log.file_name,
        settings.log.rotation,
        settings.log.retention,
    )


settings = load_config(".env")
