"""
Main FastAPI app instance declaration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination
from loguru import logger

from app.api.deps import get_redis_client
from app.api.v1.api import api_router as api_router_v1
from app.core.config import load_log_config, settings
from app.utils.celery_utils import create_celery


# Initialize the application and create a FastAPI instance
def create_application() -> FastAPI:
    # Load the log configuration
    load_log_config()
    logger.info("Starting application")

    # Create an instance of FastAPI
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        openapi_url="/openapi.json",
        docs_url="/",
    )

    # Create a celery instance and set it as an attribute of the app
    app.celery_app = create_celery()

    # Add SQLAlchemyMiddleware to the application
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

    # If there are any CORS enabled origins, add a CORSMiddleware to the application
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include the API router
    app.include_router(api_router_v1, prefix=settings.API_PREFIX)

    # Add pagination to the application
    add_pagination(app)

    return app


# Create the application
app = create_application()

# Get the celery instance
celery = app.celery_app


@app.on_event("startup")
async def startup_event():
    redis_client = await get_redis_client()
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    logger.info("Starting up...")
    # init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
