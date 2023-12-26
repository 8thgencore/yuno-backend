from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel


class TaskBase(SQLModel):
    name: str
    done: bool = Field(default=False)
    deadline: datetime | None = Field(default=None, description="ISO 8601 format")


class Task(BaseUUIDModel, TaskBase, table=True):
    created_by_id: UUID | None = Field(default=None, foreign_key="User.id")

    project_id: UUID | None = Field(default=None, foreign_key="Project.id")
    project: Optional["Project"] = Relationship(  # noqa: F821
        back_populates="tasks",
        sa_relationship_kwargs={"lazy": "joined"},
    )
