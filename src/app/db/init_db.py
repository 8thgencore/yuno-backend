from typing import Dict, List

from sqlmodel.ext.asyncio.session import AsyncSession

from app import crud
from app.schemas.role_schema import IRoleCreate
from app.schemas.user_schema import IUserCreate

roles: List[IRoleCreate] = [
    IRoleCreate(name="admin", description="Admin role"),
    IRoleCreate(name="manager", description="Manager role"),
    IRoleCreate(name="user", description="User role"),
]

users: List[Dict[str, str | IUserCreate]] = [
    {
        "data": IUserCreate(
            first_name="Admin",
            last_name="FastAPI",
            email="admin@example.com",
            username="admin",
            password="qwerty",
            is_superuser=True,
        ),
        "role": "admin",
    },
    {
        "data": IUserCreate(
            first_name="Manager",
            last_name="FastAPI",
            email="manager@example.com",
            username="manager",
            password="qwerty",
            is_superuser=False,
        ),
        "role": "manager",
    },
    {
        "data": IUserCreate(
            first_name="User",
            last_name="FastAPI",
            email="user@example.com",
            username="user",
            password="qwerty",
            is_superuser=False,
        ),
        "role": "user",
    },
]


async def init_db(db_session: AsyncSession) -> None:
    for role in roles:
        role_current = await crud.role.get_role_by_name(name=role.name, db_session=db_session)
        if not role_current:
            await crud.role.create(obj_in=role, db_session=db_session)

    for user in users:
        current_user = await crud.user.get_by_email(
            email=user["data"].email, db_session=db_session
        )
        role = await crud.role.get_role_by_name(name=user["role"], db_session=db_session)
        if not current_user:
            user["data"].role_id = role.id
            await crud.user.create_with_role(obj_in=user["data"], db_session=db_session)
