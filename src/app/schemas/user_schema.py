from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.user_model import UserBase
from app.schemas.media_schema import IImageMediaRead
from app.schemas.role_schema import IRoleRead
from app.utils.partial import optional


class IUserCreate(UserBase):
    password: Optional[str]

    class Config:
        hashed_password = None


# All these fields are optional
@optional
class IUserUpdate(UserBase):
    pass


class IUserRead(UserBase):
    id: UUID
    image: Optional[IImageMediaRead] = Field(..., repr=True)


class IUserReadWithRole(UserBase):
    id: UUID
    role: Optional[IRoleRead] = None
    image: Optional[IImageMediaRead] = Field(..., repr=True)

    # image_url: Optional[str]
    # @validator("image_url", pre=True, check_fields=False, always=True)
    # # Always true because link does not exist in the database
    # def get_image_url(cls, value: Any, values: Any) -> str:
    #     if "image" in values:
    #         if values["image"] is None:
    #             return ""

    #         url = values["image"].media.link
    #         return url

    # class Config:
    #     fields = {"image": {"exclude": True}}


class IUserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
