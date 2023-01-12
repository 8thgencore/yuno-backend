from typing import List, Optional
from uuid import UUID

from app.models.project_model import ProjectBase
from app.schemas.user_schema import IUserRead
from app.utils.partial import optional


class IProjectCreate(ProjectBase):
    pass


@optional
class IProjectUpdate(ProjectBase):
    pass


class IProjectRead(ProjectBase):
    id: UUID


class IProjectWithUsers(ProjectBase):
    id: UUID
    users: Optional[List[IUserRead]] = []
