from sqlmodel import SQLModel

from app.models.base_uuid_model import BaseUUIDModel


class MediaBase(SQLModel):
    title: str | None
    description: str | None
    path: str | None


class Media(BaseUUIDModel, MediaBase, table=True):
    pass
