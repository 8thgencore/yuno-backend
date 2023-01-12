from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base_uuid_model import SQLModel


class ProjectUserLink(SQLModel, table=True):
    project_id: Optional[UUID] = Field(
        default=None, nullable=False, foreign_key="Project.id", primary_key=True
    )
    user_id: Optional[UUID] = Field(
        default=None, nullable=False, foreign_key="User.id", primary_key=True
    )
    joined_at: Optional[datetime] = Field(default=datetime.now())

    user: "User" = Relationship(back_populates="project_links")  # noqa: F821
    project: "Project" = Relationship(back_populates="user_links")  # noqa: F821
