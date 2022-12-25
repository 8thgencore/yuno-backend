from typing import Any, AsyncGenerator, Callable, List
from uuid import UUID

import aioredis
from aioredis import Redis
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from app import crud
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user_model import User
from app.schemas.auth_schema import IAuthRegister
from app.schemas.common_schema import IMetaGeneral, TokenType
from app.schemas.user_schema import IUserCreate, IUserRead
from app.utils.token import get_valid_tokens

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/token",
    scheme_name="JWT",
)


async def get_redis_client() -> Redis:
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
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


def get_current_user(required_roles: List[str] = None) -> User:
    async def current_user(
        token: str = Depends(reusable_oauth2),
        redis_client: Redis = Depends(get_redis_client),
    ) -> User:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user_id = payload["sub"]
        valid_access_tokens = await get_valid_tokens(redis_client, user_id, TokenType.ACCESS)
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

        if required_roles:
            is_valid_role = False
            for role in required_roles:
                if role == user.role.name:
                    is_valid_role = True

            if not is_valid_role:
                raise HTTPException(
                    status_code=403,
                    detail=f"""Role "{required_roles}" is required for this action""",
                )

        return user

    return current_user


async def user_exists(user: IUserCreate) -> IUserCreate:
    is_user = await crud.user.get_by_email(email=user.email)
    if is_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same email",
        )
    is_user = await crud.user.get_by_username(username=user.username)
    if is_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same username",
        )
    return user


async def is_valid_user(user_id: UUID) -> IUserRead:
    user = await crud.user.get(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User no found")

    return


def update_schema_name(app: FastAPI, function: Callable, name: str) -> None:
    """
    Updates the Pydantic schema name for a FastAPI function that takes
    in a fastapi.UploadFile = File(...) or bytes = File(...).

    This is a known issue that was reported on FastAPI#1442 in which
    the schema for file upload routes were auto-generated with no
    customization options. This renames the auto-generated schema to
    something more useful and clear.

    Args:
        app: The FastAPI application to modify.
        function: The function object to modify.
        name: The new name of the schema.
    """
    for route in app.routes:
        if route.endpoint is function:
            route.body_field.type_.__name__ = name
            break
