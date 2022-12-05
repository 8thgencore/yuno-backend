"""
Main FastAPI app instance declaration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import config, load_log_config

from app.api import ping


# Initialize the application
def create_application() -> FastAPI:
    load_log_config()
    logger.info("Starting application")

    app = FastAPI(
        title=config.app.title,
        version=config.app.version,
        description=config.app.description,
        openapi_url="/openapi.json",
        docs_url="/",
    )

    # Set all CORS enabled origins
    if config.app.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in config.app.cors_origins],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(ping.router)
    # app.include_router(api_router)

    return app


app = create_application()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    # init_db(app)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
