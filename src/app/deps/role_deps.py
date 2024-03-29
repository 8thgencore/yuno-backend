from typing import Annotated
from uuid import UUID

from fastapi import Path, Query

from app import repository
from app.models.role_model import Role
from app.utils.exceptions.common_exception import (
    IdNotFoundException,
    NameNotFoundException,
)


async def get_role_by_name(
    role_name: Annotated[str, Query(title="String compare with name or last name")] = "",
) -> Role:
    role = await repository.role.get_role_by_name(name=role_name)
    if not role:
        raise NameNotFoundException(Role, name=role_name)
    return role


async def get_role_by_id(role_id: Annotated[UUID, Path(title="The UUID id of the role")]) -> Role:
    role = await repository.role.get(id=role_id)
    if not role:
        raise IdNotFoundException(Role, id=role_id)
    return role
