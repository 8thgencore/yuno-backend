from typing import Optional
from uuid import UUID

from app.models.user_model import UserBase


class IUserCreate(UserBase):
    password: Optional[str]

    class Config:
        hashed_password = "Main"


class IUserUpdate(UserBase):
    pass


class IUserRead(UserBase):
    id: UUID
