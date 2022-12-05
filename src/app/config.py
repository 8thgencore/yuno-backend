from dataclasses import dataclass, fields
from datetime import datetime, time, timedelta
from functools import lru_cache
from typing import List

from environs import Env

from app import logging


@dataclass
class Application:
    title: str
    version: str
    description: str
    cors_origins: List[str]


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int
    uri: str = ""

    def __post_init__(self) -> None:
        self.uri = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class RedisConfig:
    host: str
    port: int
    password: str
    pool_size: int


@dataclass
class LogConfig:
    file_name: str
    rotation: time
    retention: timedelta


@dataclass
class Miscellaneous:
    pass


@dataclass
class Config:
    app: Application
    db: DbConfig
    redis: RedisConfig
    log: LogConfig
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
            host=env.str("DB_HOST"),
            password=env.str("DB_PASS"),
            user=env.str("DB_USER"),
            database=env.str("DB_NAME"),
            port=env.int("DB_PORT"),
        ),
        redis=RedisConfig(
            host=env.str("REDIS_HOST"),
            password=env.str("REDIS_PASS"),
            port=env.int("REDIS_PORT"),
            pool_size=env.int("REDIS_POOL_SIZE"),
        ),
        log=LogConfig(
            file_name=env.str("LOG_FILE_NAME"),
            rotation=datetime.strptime(env.str("LOG_ROTATION"), "%H:%M").time(),
            retention=timedelta(days=env.int("LOG_RETENTION")),
        ),
        misc=Miscellaneous(),
    )


@lru_cache()
def load_log_config():
    logging.setup(
        config.log.file_name,
        config.log.rotation,
        config.log.retention,
    )


config = load_config('.env')
