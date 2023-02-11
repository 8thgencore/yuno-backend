from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import ProjectUserLink
from app.models.user_model import User


class ProjectBase(SQLModel):
    name: str
    description: str
    link: str


class Project(BaseUUIDModel, ProjectBase, table=True):
    # created_by_id: Optional[UUID] = Field(default=None, foreign_key="User.id")
    created_by_id: Optional[UUID] = Field(default=None)

    users: List["User"] = Relationship(  # noqa: F821
        back_populates="projects",
        link_model=ProjectUserLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    tasks: List["Task"] = Relationship(  # noqa: F821
        back_populates="project",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "order_by": "asc(Task.done)",
        },
    )
