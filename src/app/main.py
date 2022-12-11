"""
Main FastAPI app instance declaration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from loguru import logger

from app.api import ping
from app.api.deps import get_redis_client
from app.api.v1.api import api_router as api_router_v1
from app.core.config import load_log_config, settings


# Initialize the application
def create_application() -> FastAPI:
    load_log_config()
    logger.info("Starting application")

    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        openapi_url="/openapi.json",
        docs_url="/",
    )

    app.add_middleware(
        SQLAlchemyMiddleware,
        db_url=settings.ASYNC_DB_URI,
        engine_args={
            "echo": False,
            "pool_pre_ping": True,
            "pool_size": 4,
            "max_overflow": 64,
        },
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(ping.router)
    app.include_router(api_router_v1, prefix=settings.API_PREFIX)

    return app


app = create_application()


@app.on_event("startup")
async def startup_event():
    redis_client = await get_redis_client()
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    logger.info("Starting up...")
    # init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
