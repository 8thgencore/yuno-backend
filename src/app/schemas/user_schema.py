from enum import Enum
from uuid import UUID

from pydantic import ConfigDict, Field

from app.models.user_model import UserBase
from app.schemas.image_media_schema import IImageMediaRead
from app.schemas.role_schema import IRoleRead
from app.utils.partial import optional


class IUserCreate(UserBase):
    password: str | None
    model_config = ConfigDict(hashed_password=None)


# All these fields are optional
@optional
class IUserUpdate(UserBase):
    pass


class IUserRead(UserBase):
    id: UUID
    image: IImageMediaRead | None = Field(..., repr=True)


class IUserWithoutImage(UserBase):
    id: UUID


class IUserReadWithRole(UserBase):
    id: UUID
    role: IRoleRead | None = None
    image: IImageMediaRead | None = Field(..., repr=True)


class IUserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
