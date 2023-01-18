from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params

from app import crud
from app.api import deps
from app.models import Project, User
from app.schemas.project_schema import (
    IProjectCreate,
    IProjectRead,
    IProjectUpdate,
    IProjectWithUsers,
)
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    create_response,
)
from app.utils.exceptions import IdNotFoundException, UserNotCreatorProject, UserNotMemberProject
from app.utils.exceptions.project_exception import UserAlredyMemberProject

router = APIRouter()


@router.get("/my")
async def get_my_projects(
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IProjectWithUsers]:
    """
    Get my projects
    """
    projects = await crud.project.get_by_user(user=current_user)
    return create_response(data=projects)


@router.get("/list")
async def read_project_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IProjectRead]:
    """
    Gets a projects list
    """
    projects = await crud.project.get_multi_paginated(params=params)
    return create_response(data=projects)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    new_project: IProjectCreate,
    current_user: User = Depends(deps.get_current_user()),
) -> IPostResponseBase[IProjectRead]:
    """
    Creates a new project
    """
    project = await crud.project.create(obj_in=new_project, user=current_user)
    return create_response(data=project)


@router.get("/{project_id}")
async def get_project_by_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IProjectWithUsers]:
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

    if current_user not in current_project.users:
        raise UserNotMemberProject()

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


@router.get("/{project_id}/join")
async def join_to_project_by_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IProjectWithUsers]:
    """
    Join the project
    """
    current_project = await crud.project.get(id=project_id)
    if not current_project:
        raise IdNotFoundException(Project, id=project_id)

    if current_user in current_project.users:
        raise UserAlredyMemberProject()

    project = await crud.project.join_the_project(user=current_user, project=current_project)
    return create_response(data=project)


@router.get("/{project_id}/leave")
async def leave_to_project_by_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IProjectWithUsers]:
    """
    Leave the project
    """
    current_project = await crud.project.get(id=project_id)
    if not current_project:
        raise IdNotFoundException(Project, id=project_id)

    if current_user not in current_project.users:
        raise UserNotMemberProject()

    project = await crud.project.leave_the_project(user=current_user, project=current_project)
    return create_response(data=project)
