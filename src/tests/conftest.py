import asyncio
from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.db.session import get_async_session, metadata
from app.main import app

# =============================
# > Database settings
# =============================
database_url = settings.ASYNC_DB_URI.rsplit("/", 1)[0] + "/yuno-db-test"

engine_test = create_async_engine(database_url, poolclass=NullPool)
TestingSessionLocal = sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)
metadata.bind = engine_test

# =============================


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=database_url,
    engine_args={
        "echo": False,
        "poolclass": NullPool,
    },
)


@pytest.fixture(autouse=True, scope="session")
async def prepare_database() -> AsyncGenerator[None, None]:
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


# SETUP
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================
# > Clients
# =============================
client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://web/api/v1") as ac:
        yield ac
