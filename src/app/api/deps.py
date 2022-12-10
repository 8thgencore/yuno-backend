from datetime import datetime
from typing import AsyncGenerator, List
from uuid import UUID

import aioredis
from aioredis import Redis
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from app import crud
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user_model import User
from app.schemas.common_schema import TokenType, IMetaGeneral
from app.schemas.user_schema import IUserCreate, IUserRead
from app.utils.token import get_valid_tokens
from app.utils.uuid6 import uuid6

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login", scheme_name="JWT")


async def get_redis_client() -> Redis:
    redis = aioredis.from_url(
        f"redis://{settings.redis.REDIS_HOST}:{settings.redis.REDIS_PORT}",
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )
    return redis


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_general_meta() -> IMetaGeneral:
    current_roles = await crud.role.get_multi(skip=0, limit=100)
    return IMetaGeneral(roles=current_roles)

def get_current_user() -> User:
    async def current_user(
        token: str = Depends(reusable_oauth2),
    ) -> User:
        try:
            payload = jwt.decode(token, settings.auth.SECRET_KEY, algorithms=[Security.ALGORITHM])
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user_id = payload["sub"]
        valid_access_tokens = await get_valid_tokens(
            user_id, TokenType.ACCESS
        )
        if valid_access_tokens and token not in valid_access_tokens:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user: User = await crud.user.get(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        return user

    return current_user


async def user_exists(new_user: IUserCreate) -> IUserCreate:
    user = await crud.user.get_by_email(email=new_user.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same email",
        )
    return new_user


async def is_valid_user(user_id: UUID) -> IUserRead:
    user = await crud.user.get(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User no found")

    return
