from typing import Optional
from uuid import UUID

from app.models.task_model import TaskBase
from app.utils.partial import optional


class ITaskCreate(TaskBase):
    project_id: Optional[UUID]


@optional
class ITaskUpdate(TaskBase):
    pass


class ITaskRead(TaskBase):
    id: UUID
    project_id: Optional[UUID]


class ITaskWithProjectName(TaskBase):
    id: UUID
    project_id: Optional[UUID]
    project_name: str
