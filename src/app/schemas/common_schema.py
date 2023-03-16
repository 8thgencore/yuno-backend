from enum import Enum

from pydantic import BaseModel

from app.schemas.role_schema import IRoleRead


class IMetaGeneral(BaseModel):
    roles: list[IRoleRead]


class IOrderEnum(str, Enum):
    ascendent = "asc"
    descendent = "desc"


class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"
    RESET = "reset_token"
