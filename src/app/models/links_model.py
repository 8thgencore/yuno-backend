from datetime import datetime
from uuid import UUID

from sqlmodel import Field

from app.models.base_uuid_model import SQLModel


class ProjectUserLink(SQLModel, table=True):
    project_id: UUID | None = Field(
        default=None,
        foreign_key="Project.id",
        primary_key=True,
        nullable=False,
    )
    user_id: UUID | None = Field(
        default=None,
        foreign_key="User.id",
        primary_key=True,
        nullable=False,
    )
    joined_at: datetime | None = Field(default=datetime.now())
