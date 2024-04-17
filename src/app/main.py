"""
Main FastAPI app instance declaration
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from loguru import logger

from app.api.deps import get_redis_client
from app.api.v1.api import api_router as api_router_v1
from app.core.config import settings
from app.core.logging import configure_logging
from app.utils.celery_utils import create_celery


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    redis_client = await get_redis_client()
    logger.info("Init fastapi cache")
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

    yield

    logger.info("Shutting down...")
    await FastAPICache.clear()


# Initialize the application and create a FastAPI instance
def create_application() -> FastAPI:
    # Load the log configuration
    configure_logging()
    logger.info("Starting application")

    # Create an instance of FastAPI
    app = FastAPI(
        title=settings.srv.APP_TITLE,
        version=settings.srv.APP_VERSION,
        description=settings.srv.APP_DESCRIPTION,
        openapi_url="/openapi.json",
        docs_url="/",
        lifespan=lifespan,
    )

    # Create a celery instance and set it as an attribute of the app
    app.celery_app = create_celery()

    # Add SQLAlchemyMiddleware to the application
    app.add_middleware(
        SQLAlchemyMiddleware,
        db_url=settings.database.ASYNC_DATABASE_URI,
        engine_args={
            "echo": False,
            "pool_pre_ping": True,
            "pool_size": 4,
            "max_overflow": 64,
        },
    )

    # If there are any CORS enabled origins, add a CORSMiddleware to the application
    if settings.srv.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.srv.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include the API router
    app.include_router(api_router_v1, prefix=settings.srv.API_PREFIX)

    # Add pagination to the application
    # add_pagination(app)

    return app


# Create the application
app = create_application()

# Get the celery instance
celery = app.celery_app
