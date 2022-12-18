from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Params

from app import crud
from app.api import deps
from app.models import User
from app.models.role_model import Role
from app.models.user_model import UserBase
from app.schemas.common_schema import IOrderEnum
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from app.schemas.role_schema import IRoleEnum
from app.schemas.user_schema import IUserCreate, IUserRead, IUserReadWithoutProjects, IUserUpdate
from app.utils.exceptions import IdNotFoundException, UserSelfDeleteException

router = APIRouter()


@router.get("", response_model=IGetResponseBase[IUserRead])
async def get_my_data(
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Gets my user profile information
    """
    return create_response(data=current_user)


@router.get("/list", response_model=IGetResponsePaginated[IUserReadWithoutProjects])
async def read_users_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Retrieve users. Requires admin or manager role
    """
    users = await crud.user.get_multi_paginated(params=params)
    return create_response(data=users)


@router.get("/list/by_created_at", response_model=IGetResponsePaginated[IUserReadWithoutProjects])
async def get_user_list_order_by_created_at(
    order: Optional[IOrderEnum] = Query(
        default=IOrderEnum.ascendent, description="It is optional. Default is ascendent"
    ),
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Gets a paginated list of users ordered by created datetime
    """
    users = await crud.user.get_multi_paginated_ordered(
        params=params,
        order=order,
        order_by="created_at",
    )
    return create_response(data=users)


@router.get("/{user_id}", response_model=IGetResponseBase[IUserRead])
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Gets a user by his/her id
    """
    if user := await crud.user.get(id=user_id):
        return create_response(data=user)
    else:
        raise IdNotFoundException(User, id=user_id)


@router.post("", response_model=IPostResponseBase[IUserRead], status_code=status.HTTP_201_CREATED)
async def create_user(
    new_user: IUserCreate = Depends(deps.user_exists),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Creates a new user
    """
    role = await crud.role.get(id=new_user.role_id)
    if not role:
        raise IdNotFoundException(Role, id=new_user.role_id)

    user = await crud.user.create_with_role(obj_in=new_user)
    return create_response(data=user)


@router.put("/{user_id}", response_model=IPutResponseBase[IUserRead])
async def update_user_by_id(
    user_id: UUID,
    user: IUserUpdate,
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Update a user by his/her id
    """
    current_user = await crud.user.get(id=user_id)
    if not current_user:
        raise IdNotFoundException(User, id=user_id)
    user_updated = await crud.user.update(obj_new=user, obj_current=current_user)
    return create_response(data=user_updated)


@router.delete("/{user_id}", response_model=IDeleteResponseBase[IUserRead])
async def remove_user(
    user: User = Depends(deps.is_valid_user),
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Delete a user by his/her id
    """
    if current_user.id == user.id:
        raise UserSelfDeleteException()

    user = await crud.user.remove(id=user.id)
    return create_response(data=user)
