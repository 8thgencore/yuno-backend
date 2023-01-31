from typing import List, Optional
from uuid import UUID

from app.models.project_model import ProjectBase
from app.schemas.task_schema import ITaskRead
from app.schemas.user_schema import IUserRead
from app.utils.partial import optional


class IProjectCreate(ProjectBase):
    pass


@optional
class IProjectUpdate(ProjectBase):
    pass


class IProjectRead(ProjectBase):
    id: UUID
    created_by_id: UUID


class IProjectWithUsers(ProjectBase):
    id: UUID
    created_by_id: UUID
    users: Optional[List[IUserRead]] = []


class IProjectWithUsersTasks(ProjectBase):
    id: UUID
    created_by_id: UUID
    tasks: Optional[List[ITaskRead]] = []
    users: Optional[List[IUserRead]] = []
