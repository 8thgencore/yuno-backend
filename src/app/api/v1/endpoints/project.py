from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params

from app import crud
from app.api import deps
from app.models import Project, User
from app.schemas.project_schema import IProjectCreate, IProjectRead, IProjectUpdate
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    create_response,
)
from app.utils.exceptions import IdNotFoundException, UserNotCreatorProject

router = APIRouter()


@router.get("/list")
async def read_project_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IProjectRead]:
    """
    Retrieve project. // TODO: only users projects
    """
    projects = await crud.project.get_multi_paginated(params=params)
    return create_response(data=projects)


@router.get("/{project_id}")
async def get_project_by_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IProjectRead]:
    """
    Gets a project by id
    """
    if project := await crud.project.get(id=project_id):
        return create_response(data=project)
    else:
        raise IdNotFoundException(Project, id=project_id)


@router.put("/{project_id}")
async def update_project_by_id(
    project_id: UUID,
    project: IProjectUpdate,
    current_user: User = Depends(deps.get_current_user()),
) -> IPostResponseBase[IProjectRead]:
    """
    Update a project by id
    """
    current_project = await crud.project.get(id=project_id)
    if not current_project:
        raise IdNotFoundException(Project, id=project_id)

    project_updated = await crud.project.update(obj_new=project, obj_current=current_project)
    return create_response(data=project_updated)


@router.delete("/{project_id}")
async def remove_project_by_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IDeleteResponseBase[IProjectRead]:
    """
    Delete a project by id
    """
    project = await crud.project.get(id=project_id)
    if not project:
        raise IdNotFoundException(Project, id=project_id)

    if not project.created_by_id == current_user.id:
        raise UserNotCreatorProject()

    project = await crud.project.remove(id=project_id)
    return create_response(data=project)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    new_project: IProjectCreate,
    current_user: User = Depends(deps.get_current_user()),
) -> IPostResponseBase[IProjectRead]:
    """
    Creates a new project
    """
    project = await crud.project.create(obj_in=new_project, user=current_user)
    return create_response(data=project)
