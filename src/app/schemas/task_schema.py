from uuid import UUID

from app.models.task_model import TaskBase
from app.utils.partial import optional


class ITaskCreate(TaskBase):
    pass


@optional
class ITaskUpdate(TaskBase):
    pass


class ITaskRead(TaskBase):
    id: UUID


class ITaskWithProjectName(TaskBase):
    id: UUID
    project_name: str
