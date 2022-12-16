from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field

from app.models.base_uuid_model import BaseUUIDModel


class ProjectUsers(BaseUUIDModel, table=True):
    project_id: Optional[UUID] = Field(
        default=None, nullable=False, foreign_key="Project.id", primary_key=True
    )
    user_id: Optional[UUID] = Field(
        default=None, nullable=False, foreign_key="User.id", primary_key=True
    )
    joined_at: Optional[datetime] = Field(default=datetime.now())
