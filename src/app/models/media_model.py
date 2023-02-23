from typing import Optional

from sqlmodel import SQLModel

from app.models.base_uuid_model import BaseUUIDModel


class MediaBase(SQLModel):
    title: Optional[str]
    description: Optional[str]
    path: Optional[str]


class Media(BaseUUIDModel, MediaBase, table=True):
    pass
