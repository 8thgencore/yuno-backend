from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel
from app.models.media_model import Media


class ImageMediaBase(SQLModel):
    file_format: Optional[str]
    width: Optional[int]
    height: Optional[int]


class ImageMedia(BaseUUIDModel, ImageMediaBase, table=True):
    media_id: Optional[UUID] = Field(default=None, foreign_key="Media.id")
    media: Media = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "ImageMedia.media_id==Media.id",
        }
    )
