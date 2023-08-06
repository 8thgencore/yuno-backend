from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import ModeEnum, settings

DB_POOL_SIZE = 83
WEB_CONCURRENCY = 9
POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)

connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.ASYNC_DB_URI,
    echo=True,
    future=True,
    pool_size=POOL_SIZE,
    max_overflow=64,
    # Asincio pytest works with NullPool
    poolclass=NullPool if settings.MODE == ModeEnum.testing else QueuePool,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
