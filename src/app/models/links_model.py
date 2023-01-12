from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field

from app.models.base_uuid_model import SQLModel


class ProjectUserLink(SQLModel, table=True):
    project_id: Optional[UUID] = Field(
        default=None, foreign_key="Project.id", primary_key=True, nullable=False
    )
    user_id: Optional[UUID] = Field(
        default=None, foreign_key="User.id", primary_key=True, nullable=False
    )
    joined_at: Optional[datetime] = Field(default=datetime.now())
