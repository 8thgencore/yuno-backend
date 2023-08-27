from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import ProjectUserLink
from app.models.user_model import User
from app.models.task_model import Task



class ProjectBase(SQLModel):
    name: str
    description: str
    link: str
    percent_completed: float = Field(default=0)


class Project(BaseUUIDModel, ProjectBase, table=True):
    # created_by_id: UUID | None = Field(default=None, foreign_key="User.id")
    created_by_id: UUID | None = Field(default=None)

    users: list["User"] = Relationship(  # noqa: F821
        back_populates="projects",
        link_model=ProjectUserLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    tasks: list["Task"] = Relationship(  # noqa: F821
        back_populates="project",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "order_by": "asc(Task.done)",
        },
    )
