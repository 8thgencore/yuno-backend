from fastapi_pagination import Params
from sqlalchemy.orm import selectinload
from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models import Project, ProjectUserLink, Task, User
from app.schemas.project_schema import (
    IProjectCreate,
    IProjectRead,
    IProjectUpdate,
    IProjectWithUsers,
)
from app.schemas.statistics_schema import StatisticsRead
from app.schemas.task_schema import ITaskRead


class CRUDProject(CRUDBase[Project, IProjectCreate, IProjectUpdate]):
    async def create(
        self, *, obj_in: IProjectCreate, user: User, db_session: AsyncSession | None = None
    ) -> Project:
        db_session = db_session or super().get_db().session

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
        self,
        *,
        params: Params | None = Params(),
        user: User,
        db_session: AsyncSession | None = None,
    ) -> list[IProjectWithUsers]:
        db_session = db_session or super().get_db().session

        query = (
            select(Project)
            .where(Project.users.contains(user))
            .options(selectinload(Project.users))
        )
        projects = await super().get_multi_paginated(params=params, query=query)
        return projects

    async def remove(self, *, id: str, db_session: AsyncSession | None = None) -> Project:
        db_session = db_session or super().get_db().session

        # delete links
        response = await db_session.execute(
            select(ProjectUserLink).where(ProjectUserLink.project_id == id)
        )
        obj = response.scalars().all()
        for ob in obj:
            await db_session.delete(ob)

        # delete all task project
        response = await db_session.execute(select(Task).where(Task.project_id == id))
        obj = response.scalars().all()
        for ob in obj:
            await db_session.delete(ob)

        # delete project
        response = await db_session.execute(select(Project).where(Project.id == id))
        obj = response.scalar_one()
        await db_session.delete(obj)

        await db_session.commit()
        return obj

    async def is_member_project(
        self, *, user_id: str, project_id: str, db_session: AsyncSession | None = None
    ) -> bool:
        db_session = db_session or super().get_db().session

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
        self, *, user: User, project: Project, db_session: AsyncSession | None = None
    ) -> Project:
        db_session = db_session or super().get_db().session

        project_user_link = ProjectUserLink(
            user_id=user.id,
            project_id=project.id,
        )
        db_session.add(project_user_link)
        await db_session.commit()
        await db_session.refresh(project)
        return project

    async def leave_the_project(
        self, *, user: User, project: Project, db_session: AsyncSession | None = None
    ) -> Project:
        db_session = db_session or super().get_db().session

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
        await db_session.refresh(project)
        await db_session.commit()
        return project

    async def get_tasks(
        self, *, project_id: str, db_session: AsyncSession | None = None
    ) -> list[ITaskRead]:
        db_session = db_session or super().get_db().session

        query = select(Task).where(Task.project_id == project_id)
        tasks = await super().get_multi_paginated(query=query)
        return tasks

    async def get_members(
        self, *, project: IProjectRead, db_session: AsyncSession | None = None
    ) -> list[ITaskRead]:
        db_session = db_session or super().get_db().session

        query = select(User).where(User.projects.contains(project))
        tasks = await super().get_multi_paginated(query=query)
        return tasks

    async def get_stats(self, *, db_session: AsyncSession | None = None) -> list[ITaskRead]:
        db_session = db_session or super().get_db().session

        projects_count = await super().get_count()

        result = await db_session.execute(
            select(func.count(Project.id)).where(Project.percent_completed == 0)
        )
        missing_count = result.scalar()

        result = await db_session.execute(
            select(func.count(Project.id)).where(Project.percent_completed == 1)
        )
        completed_count = result.scalar()

        stats = StatisticsRead(
            projects_count=projects_count,
            missing_count=missing_count,
            completed_count=completed_count,
            ongoing_count=projects_count - (missing_count + completed_count),
        )

        return stats


project = CRUDProject(Project)
