from enum import Enum
from typing import List, Optional
from uuid import UUID

from app.models.user_model import UserBase
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
    role: Optional[IRoleRead] = None


class IUserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
