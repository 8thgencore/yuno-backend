from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel, UTCDatetime


class TaskBase(SQLModel):
    name: str
    done: bool = Field(default=False)
    deadline: Optional[UTCDatetime] = Field(description="ISO 8601 format")
    project_id: Optional[UUID] = Field(default=None, foreign_key="Project.id")


class Task(BaseUUIDModel, TaskBase, table=True):
    created_by_id: Optional[UUID] = Field(default=None, foreign_key="User.id")
    project: Optional["Project"] = Relationship(  # noqa: F821
        back_populates="tasks",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
