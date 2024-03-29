from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params
from loguru import logger

from app import repository
from app.api import deps
from app.models import Project, Task, User
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    create_response,
)
from app.schemas.task_schema import (
    ITaskCreate,
    ITaskRead,
    ITaskUpdate,
    ITaskWithProjectName,
)
from app.utils.exceptions import (
    IdNotFoundException,
    UserNotMemberProject,
)

router = APIRouter()


@router.get("/list")
async def get_my_tasks_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[ITaskWithProjectName]:
    """Endpoint to retrieve the tasks list of the current user.

    Returns:
        A paginated response containing the tasks with the project name.
    """
    tasks = await repository.task.get_by_user(user=current_user)

    return create_response(data=tasks)


@router.get("/not_done")
async def get_my_not_completed_tasks_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[ITaskWithProjectName]:
    """Endpoint to retrieve the not completed tasks list of the current user.

    Returns:
        A paginated response containing the not completed tasks with the project name.
    """
    tasks = await repository.task.get_not_completed_by_user(user=current_user)

    return create_response(data=tasks)


@router.get("/by_deadline")
async def get_tasks_list_by_deadline(
    date: datetime,
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[ITaskWithProjectName]:
    """Endpoint to retrieve the tasks list of the current user by deadline.

    Args:
      - date: A filter to retrieve tasks by a specific deadline.

    Returns:
        A paginated response containing the tasks with the project name.
    """
    tasks = await repository.task.get_by_deadline(user=current_user, date=date)

    return create_response(data=tasks)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    new_task: ITaskCreate,
    current_user: User = Depends(deps.get_current_user()),
) -> IPostResponseBase[ITaskRead]:
    """Endpoint to create a new task.

    Args:
      - task: Task data to be created.

    Returns:
        The created task data.
    """
    if new_task.project_id:
        await check_user_member_project(user_id=current_user.id, project_id=new_task.project_id)

    task = await repository.task.create(obj_in=new_task, user=current_user)
    logger.info(f"User '{current_user.id}' created new task: '{task.id}'")

    return create_response(data=task)


@router.get("/{task_id}")
async def get_task_by_id(
    task_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[ITaskRead]:
    """Endpoint to get a task by ID.

    Args:
      - task_id: ID of the task to update.

    Returns:
        The task data.
    """
    if task := await repository.task.get(id=task_id):
        return create_response(data=task)
    else:
        raise IdNotFoundException(Task, id=task_id)


@router.put("/{task_id}")
async def update_task_by_id(
    task_id: UUID,
    task: ITaskUpdate,
    current_user: User = Depends(deps.get_current_user()),
) -> IPostResponseBase[ITaskRead]:
    """Endpoint to update a task by ID.

    Args:
      - task_id: ID of the task to update.
      - task: Task data to be updated.

    Returns:
        The updated task data.
    """
    current_task = await repository.task.get(id=task_id)
    if not current_task:
        raise IdNotFoundException(Task, id=task_id)

    if current_task.project_id:
        await check_user_member_project(
            user_id=current_user.id,
            project_id=current_task.project_id,
        )

    task_updated = await repository.task.update(obj_new=task, obj_current=current_task)
    logger.info(f"User '{current_user.id}' updated task: '{task_id}'")

    return create_response(data=task_updated)


@router.delete("/{task_id}")
async def remove_task_by_id(
    task_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IDeleteResponseBase[ITaskRead]:
    """Endpoint to delete a task by ID.

    Args:
      - task_id: ID of the task to delete.

    Returns:
        The deleted task data.
    """
    current_task = await repository.task.get(id=task_id)
    if not current_task:
        raise IdNotFoundException(Task, id=task_id)

    await check_user_member_project(user_id=current_user.id, project_id=current_task.project_id)

    task = await repository.task.remove(id=task_id)
    logger.info(f"User '{current_user.id}' deleted task: '{task_id}'")

    return create_response(data=task)


async def check_user_member_project(user_id: str, project_id: str) -> None:
    """Check whether the user is a member of the project."""
    project = await repository.project.get(id=project_id)
    if not project:
        raise IdNotFoundException(Project, id=project_id)

    is_member = await repository.project.is_member_project(user_id=user_id, project_id=project_id)
    if not is_member:
        raise UserNotMemberProject()
