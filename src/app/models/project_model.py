from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel
from app.models.project_user_model import ProjectUserLink


class ProjectBase(SQLModel):
    name: str
    description: str
    link: str


class Project(BaseUUIDModel, ProjectBase, table=True):
    created_by_id: Optional[UUID] = Field(default=None, foreign_key="User.id")
    # created_by_id: Optional[UUID] = Field(default=None)

    user_links: List[ProjectUserLink] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete"},
    )
