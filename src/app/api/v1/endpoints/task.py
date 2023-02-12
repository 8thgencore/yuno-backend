from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params

from app import crud
from app.api import deps
from app.models import Project, Task, User
from app.models.base_uuid_model import UTCDatetime
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
    """
    Endpoint to retrieve the tasks list of the current user.

    Returns:
        A paginated response containing the tasks with the project name.
    """
    tasks = await crud.task.get_by_user(user=current_user)
    return create_response(data=tasks)


@router.get("/not_done")
async def get_my_not_done_tasks_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[ITaskWithProjectName]:
    """
    Endpoint to retrieve the not done tasks list of the current user.

    Returns:
        A paginated response containing the not done tasks with the project name.
    """
    tasks = await crud.task.get_not_done_by_user(user=current_user)
    return create_response(data=tasks)


@router.get("/by_deadline")
async def get_tasks_list_by_deadline(
    date: UTCDatetime,
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[ITaskWithProjectName]:
    """
    Endpoint to retrieve the tasks list of the current user by deadline.

    Args:
      - date: A filter to retrieve tasks by a specific deadline.

    Returns:
        A paginated response containing the tasks with the project name.
    """
    tasks = await crud.task.get_by_deadline(user=current_user, date=date)
    return create_response(data=tasks)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    task: ITaskCreate,
    current_user: User = Depends(deps.get_current_user()),
) -> IPostResponseBase[ITaskRead]:
    """
    Endpoint to create a new task.

    Args:
      - task: Task data to be created.

    Returns:
        The created task data.
    """
    if task.project_id:
        await check_user_member_project(user_id=current_user.id, project_id=task.project_id)

    new_task = await crud.task.create(obj_in=task, user=current_user)
    return create_response(data=new_task)


@router.get("/{task_id}")
async def get_task_by_id(
    task_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[ITaskRead]:
    """
    Endpoint to get a task by ID.

    Args:
      - task_id: ID of the task to update.

    Returns:
        The task data.
    """
    if task := await crud.task.get(id=task_id):
        return create_response(data=task)
    else:
        raise IdNotFoundException(Task, id=task_id)


@router.put("/{task_id}")
async def update_task_by_id(
    task_id: UUID,
    task: ITaskUpdate,
    current_user: User = Depends(deps.get_current_user()),
) -> IPostResponseBase[ITaskRead]:
    """
    Endpoint to update a task by ID.

    Args:
      - task_id: ID of the task to update.
      - task: Task data to be updated.

    Returns:
        The updated task data.
    """
    current_task = await crud.task.get(id=task_id)
    if not current_task:
        raise IdNotFoundException(Task, id=task_id)

    if current_task.project_id:
        await check_user_member_project(
            user_id=current_user.id, project_id=current_task.project_id
        )

    task_updated = await crud.task.update(obj_new=task, obj_current=current_task)
    return create_response(data=task_updated)


@router.delete("/{task_id}")
async def remove_task_by_id(
    task_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IDeleteResponseBase[ITaskRead]:
    """
    Endpoint to delete a task by ID.

    Args:
      - task_id: ID of the task to delete.

    Returns:
        The deleted task data.
    """
    current_task = await crud.task.get(id=task_id)
    if not current_task:
        raise IdNotFoundException(Task, id=task_id)

    await check_user_member_project(user_id=current_user.id, project_id=current_task.project_id)

    task = await crud.task.remove(id=task_id)
    return create_response(data=task)


async def check_user_member_project(user_id: str, project_id: str) -> None:
    """
    Check whether the user is a member of the project
    """
    project = await crud.project.get(id=project_id)
    if not project:
        raise IdNotFoundException(Project, id=project_id)

    is_member = await crud.project.is_member_project(user_id=user_id, project_id=project_id)
    if not is_member:
        raise UserNotMemberProject()
