from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params
from loguru import logger

from app import crud
from app.api import deps
from app.models import Project, User
from app.schemas.project_schema import (
    IProjectCreate,
    IProjectRead,
    IProjectUpdate,
    IProjectWithUsers,
    IProjectWithUsersTasks,
)
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    create_response,
)
from app.schemas.task_schema import ITaskRead
from app.schemas.user_schema import IUserRead
from app.utils.exceptions import (
    IdNotFoundException,
    UserNotCreatorProject,
    UserNotMemberProject,
)
from app.utils.exceptions.project_exception import UserAlredyMemberProject

router = APIRouter()


@router.get("/me")
async def get_my_projects(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IProjectWithUsers]:
    """
    Endpoint for getting the projects of the authenticated user
    """
    projects = await crud.project.get_by_user(params=params, user=current_user)
    return create_response(data=projects)


@router.get("/list")
async def read_project_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IProjectWithUsers]:
    """
    Endpoint for getting a list of projects
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
    logger.info(f"User '{current_user.id}' created new project: '{project.id}'")

    return create_response(data=project)


@router.get("/{project_id}")
async def get_project_by_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IProjectWithUsersTasks]:
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
    logger.info(f"User '{current_user.id}' updated project: '{project_id}'")

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
    logger.info(f"User '{current_user.id}' deleted project: '{project_id}'")

    return create_response(data=project)


@router.get("/{project_id}/join")
async def join_to_project_by_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IProjectWithUsers]:
    """
    Endpoint for a user to join a project
    """
    current_project = await crud.project.get(id=project_id)
    if not current_project:
        raise IdNotFoundException(Project, id=project_id)

    if current_user in current_project.users:
        raise UserAlredyMemberProject()

    project = await crud.project.join_the_project(user=current_user, project=current_project)
    logger.info(f"User '{current_user.id}' join a project: '{project_id}'")

    return create_response(data=project)


@router.get("/{project_id}/leave")
async def leave_to_project_by_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IProjectWithUsers]:
    """
    Endpoint for a user to leave a project
    """
    current_project = await crud.project.get(id=project_id)
    if not current_project:
        raise IdNotFoundException(Project, id=project_id)

    if current_user not in current_project.users:
        raise UserNotMemberProject()

    project = await crud.project.leave_the_project(user=current_user, project=current_project)
    logger.info(f"User '{current_user.id}' leave a project: '{project_id}'")

    return create_response(data=project)


@router.get("/{project_id}/tasks")
async def tasks_list_by_project_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[ITaskRead]:
    """
    This endpoint allows getting a list of tasks associated with a project.
    """
    current_project = await crud.project.get(id=project_id)
    if not current_project:
        raise IdNotFoundException(Project, id=project_id)

    tasks = await crud.project.get_tasks(project_id=project_id)
    return create_response(data=tasks)


@router.get("/{project_id}/members")
async def members_list_by_project_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IUserRead]:
    """
    This endpoint allows getting a list of members associated with a project.
    """
    current_project = await crud.project.get(id=project_id)
    if not current_project:
        raise IdNotFoundException(Project, id=project_id)

    projects = await crud.project.get_members(project=current_project)
    return create_response(data=projects)
