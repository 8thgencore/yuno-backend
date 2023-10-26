from uuid import UUID

from fastapi import HTTPException, Path, status
from typing import Annotated

from app import crud
from app.models.user_model import User
from app.schemas.user_schema import IUserCreate, IUserRead
from app.utils.exceptions import IdNotFoundException


async def user_exists(user: IUserCreate) -> IUserCreate:
    await email_exists(user=user)
    await username_exists(user=user)
    return user


async def email_exists(user: IUserCreate) -> IUserCreate:
    is_user = await crud.user.get_by_email(email=user.email)
    if is_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same email",
        )
    return


async def username_exists(user: IUserCreate) -> IUserCreate:
    is_user = await crud.user.get_by_username(username=user.username)
    if is_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same username",
        )
    return


async def is_valid_user(
    user_id: Annotated[UUID, Path(title="The UUID id of the user")]
) -> IUserRead:
    user = await crud.user.get(id=user_id)
    if not user:
        raise IdNotFoundException(User, id=user_id)

    return user
