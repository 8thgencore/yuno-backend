from enum import Enum
from uuid import UUID

from app.models.role_model import RoleBase


class IRoleCreate(RoleBase):
    pass


class IRoleUpdate(RoleBase):
    pass


class IRoleRead(RoleBase):
    id: UUID


class IRoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"
