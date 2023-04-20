from sqlmodel import SQLModel

from app import api
from app.core.config import settings
from app.models.base_uuid_model import BaseUUIDModel
from app.utils.minio_client import MinioClient


class MediaBase(SQLModel):
    title: str | None
    description: str | None
    path: str | None


class Media(BaseUUIDModel, MediaBase, table=True):
    @property
    def link(self) -> str | None:
        if self.path is None:
            return ""
        minio: MinioClient = api.deps.minio_auth()
        url = minio.presigned_get_object(bucket_name=settings.MINIO_BUCKET, object_name=self.path)
        return url
