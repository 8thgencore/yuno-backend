from typing import List, Optional

from fastapi_async_sqlalchemy import db
from sqlalchemy.orm import selectinload
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models import Project, ProjectUserLink, Task, User
from app.schemas.project_schema import (
    IProjectCreate,
    IProjectUpdate,
    IProjectWithUsers,
)
from app.schemas.task_schema import (
    ITaskRead,
)


class CRUDProject(CRUDBase[Project, IProjectCreate, IProjectUpdate]):
    async def create(
        self, *, obj_in: IProjectCreate, user: User, db_session: Optional[AsyncSession] = None
    ) -> Project:
        db_session = db_session or db.session

        db_obj = Project.from_orm(obj_in)
        db_obj.created_by_id = user.id
        db_session.add(db_obj)
        await db_session.commit()

        project_user_link = ProjectUserLink(
            user_id=user.id,
            project_id=db_obj.id,
        )
        db_session.add(project_user_link)
        await db_session.commit()

        await db_session.refresh(db_obj)
        return db_obj

    async def get_by_user(
        self, *, user: User, db_session: Optional[AsyncSession] = None
    ) -> List[IProjectWithUsers]:
        db_session = db_session or db.session
        query = (
            select(Project)
            .where(Project.users.contains(user))
            .options(selectinload(Project.users))
        )
        projects = await super().get_multi_paginated(query=query)
        return projects

    async def is_member_project(
        self, *, user_id: str, project_id: str, db_session: Optional[AsyncSession] = None
    ) -> bool:
        db_session = db_session or db.session
        query = select(ProjectUserLink).where(
            and_(
                ProjectUserLink.user_id == user_id,
                ProjectUserLink.project_id == project_id,
            )
        )
        response = await db_session.execute(query)
        obj = response.scalar_one_or_none()

        return True if obj else False

    async def join_the_project(
        self, *, user: User, project: Project, db_session: Optional[AsyncSession] = None
    ) -> Project:
        db_session = db_session or db.session
        project_user_link = ProjectUserLink(
            user_id=user.id,
            project_id=project.id,
        )
        db_session.add(project_user_link)
        await db_session.commit()
        await db.session.refresh(project)
        return project

    async def leave_the_project(
        self, *, user: User, project: Project, db_session: Optional[AsyncSession] = None
    ) -> Project:
        db_session = db_session or db.session

        response = await db_session.execute(
            select(ProjectUserLink).where(
                and_(
                    ProjectUserLink.user_id == user.id,
                    ProjectUserLink.project_id == project.id,
                )
            )
        )
        obj = response.scalar_one_or_none()
        if obj:
            await db_session.delete(obj)
        await db.session.refresh(project)
        await db_session.commit()
        return project

    async def get_tasks(
        self, *, project_id: str, db_session: Optional[AsyncSession] = None
    ) -> List[ITaskRead]:
        db_session = db_session or db.session

        query = select(Task).where(Task.project_id == project_id)
        tasks = await super().get_multi_paginated(query=query)
        return tasks


project = CRUDProject(Project)
