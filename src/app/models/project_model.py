from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel


class ProjectBase(SQLModel):
    name: str
    description: str
    link: str


class Project(BaseUUIDModel, ProjectBase, table=True):
    created_by_id: Optional[UUID] = Field(default=None, foreign_key="User.id")
    created_by: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "Project.created_by_id==User.id",
        }
    )
