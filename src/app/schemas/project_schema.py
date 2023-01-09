from uuid import UUID

from app.models.project_model import ProjectBase
from app.utils.partial import optional


class IProjectCreate(ProjectBase):
    pass


@optional
class IProjectUpdate(ProjectBase):
    pass


class IProjectRead(ProjectBase):
    id: UUID
