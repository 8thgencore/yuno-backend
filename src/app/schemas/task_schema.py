from uuid import UUID

from app.models.task_model import TaskBase
from app.utils.partial import optional


class ITaskCreate(TaskBase):
    project_id: UUID | None


# All these fields are optional
@optional()
class ITaskUpdate(TaskBase):
    pass


class ITaskRead(TaskBase):
    id: UUID
    project_id: UUID | None


class ITaskWithProjectName(TaskBase):
    id: UUID
    project_id: UUID | None
    project_name: str | None
