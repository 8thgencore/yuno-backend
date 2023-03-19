import os
from io import BytesIO

from fastapi import APIRouter, Body, Depends, File, Query, Response, UploadFile, status
from fastapi_pagination import Params
from loguru import logger

from app import crud
from app.api import deps
from app.deps import user_deps
from app.models import User
from app.models.role_model import Role
from app.schemas.common_schema import IOrderEnum
from app.schemas.media_schema import IMediaCreate
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from app.schemas.role_schema import IRoleEnum
from app.schemas.user_schema import IUserCreate, IUserRead, IUserUpdate
from app.tasks import generate_avatar_thumbnail
from app.utils.exceptions import IdNotFoundException, UserSelfDeleteException
from app.utils.minio_client import MinioClient
from app.utils.resize_image import modify_image
from app.utils.uuid6 import uuid7

router = APIRouter()


@router.get("")
async def get_my_data(
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IUserRead]:
    """Gets my user profile information."""

    return create_response(data=current_user)


@router.put("")
async def update_my_data(
    user: IUserUpdate,
    current_user: User = Depends(deps.get_current_user()),
) -> IPutResponseBase[IUserRead]:
    """Update my user profile information."""
    if current_user.email != user.email:
        await user_deps.email_exists(user=user)
    if current_user.username != user.username:
        await user_deps.username_exists(user=user)

    user_updated = await crud.user.update(obj_new=user, obj_current=current_user)
    logger.info(f"User '{current_user.id}' updated profile information")

    return create_response(data=user_updated)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: IUserCreate = Depends(user_deps.user_exists),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
) -> IPostResponseBase[IUserRead]:
    """Creates a new user.

    Required roles:
      - admin
    """
    role = await crud.role.get(id=user.role_id)
    if not role:
        raise IdNotFoundException(Role, id=user.role_id)

    user = await crud.user.create_with_role(obj_in=user)

    return create_response(data=user)


@router.get("/list")
async def read_users_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IUserRead]:
    """Retrieve users. Requires admin or manager role."""
    users = await crud.user.get_multi_paginated(params=params)

    return create_response(data=users)


@router.get("/list/by_created_at")
async def get_user_list_order_by_created_at(
    order: IOrderEnum
    | None = Query(
        default=IOrderEnum.ascendent,
        description="It is optional. Default is ascendent",
    ),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IUserRead]:
    """Gets a paginated list of users ordered by created datetime."""
    users = await crud.user.get_multi_paginated_ordered(
        params=params,
        order=order,
        order_by="created_at",
    )

    return create_response(data=users)


@router.get("/{user_id}")
async def get_user_by_id(
    user: User = Depends(user_deps.is_valid_user),  # user_id
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IUserRead]:
    """
    Gets a user by his/her id."""
    return create_response(data=user)


@router.put("/{user_id}")
async def update_user_by_id(
    user: IUserUpdate,
    updated_user: User = Depends(user_deps.is_valid_user),  # user_id
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
) -> IPutResponseBase[IUserRead]:
    """Update a user by his/her id.

    Required roles:
      - admin
    """
    if updated_user.email != user.email:
        await user_deps.email_exists(user=user)
    if updated_user.username != user.username:
        await user_deps.username_exists(user=user)

    user_updated = await crud.user.update(obj_new=user, obj_current=updated_user)

    return create_response(data=user_updated)


@router.delete("/{user_id}")
async def remove_user_by_id(
    user: User = Depends(user_deps.is_valid_user),  # user_id
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
) -> IDeleteResponseBase[IUserRead]:
    """Delete a user by his/her id.

    Required roles:
      - admin
    """
    if current_user.id == user.id:
        raise UserSelfDeleteException()

    user = await crud.user.remove(id=user.id)

    return create_response(data=user, message="User removed")


@router.post("/image")
async def upload_my_image(
    title: str | None = Body(None),
    description: str | None = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user()),
    minio_client: MinioClient = Depends(deps.minio_auth),
) -> IPostResponseBase[IUserRead]:
    """Uploads a user image."""
    try:
        image_bytes = BytesIO(image_file.file.read())
        image_modified = modify_image(image_bytes)

        file_name_split = os.path.splitext(image_file.filename)
        file_name = f"{uuid7()}{file_name_split[-1]}"

        data_file = minio_client.put_object(
            file_name=file_name,
            file_data=BytesIO(image_modified.file_data),
            content_type=image_file.content_type,
        )

        # Add to Database
        media = IMediaCreate(title=title, description=description, path=data_file.file_name)
        user = await crud.user.update_photo(
            user=current_user,
            image=media,
            heigth=image_modified.height,
            width=image_modified.width,
            file_format=image_modified.file_format,
        )
        logger.info(f"User '{current_user.id}' updated profile image")

        generate_avatar_thumbnail.delay(current_user.id, data_file.file_name)

        return create_response(data=user)

    except Exception as e:
        logger.error(e)
        return Response("Internal server error", status_code=500)


@router.post("/{user_id}/image")
async def upload_user_image(
    user: User = Depends(user_deps.is_valid_user),  # user_id
    title: str | None = Body(None),
    description: str | None = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
    minio_client: MinioClient = Depends(deps.minio_auth),
) -> IPostResponseBase[IUserRead]:
    """Uploads a user image by his/her id.

    Required roles:
      - admin
    """
    try:
        image_modified = modify_image(BytesIO(image_file.file.read()))
        data_file = minio_client.put_object(
            file_name=image_file.filename,
            file_data=BytesIO(image_modified.file_data),
            content_type=image_file.content_type,
        )
        media = IMediaCreate(title=title, description=description, path=data_file.file_name)
        user = await crud.user.update_photo(
            user=user,
            image=media,
            heigth=image_modified.height,
            width=image_modified.width,
            file_format=image_modified.file_format,
        )

        return create_response(data=user)

    except Exception as e:
        logger.error(e)
        return Response("Internal server error", status_code=500)
