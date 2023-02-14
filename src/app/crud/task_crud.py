from datetime import datetime
from typing import List, Optional

from fastapi_async_sqlalchemy import db
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models import Project, Task, User
from app.models.base_uuid_model import UTCDatetime
from app.schemas.task_schema import ITaskCreate, ITaskUpdate, ITaskWithProjectName


class CRUDTask(CRUDBase[Task, ITaskCreate, ITaskUpdate]):
    async def create(
        self, *, obj_in: ITaskCreate, user: User, db_session: Optional[AsyncSession] = None
    ) -> Task:
        db_session = db_session or db.session

        db_obj = Task.from_orm(obj_in)
        db_obj.created_by_id = user.id
        db_session.add(db_obj)

        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def get_by_user(
        self, *, user: User, db_session: Optional[AsyncSession] = None
    ) -> List[ITaskWithProjectName]:
        db_session = db_session or db.session

        # get user projects
        query = select(Project.id).where(Project.users.contains(user))
        response = await db_session.execute(query)
        projects = response.scalars().all()

        # get user tasks
        query = (
            select(
                Task.id,
                Task.name,
                Task.deadline,
                Task.done,
                Task.project_id,
                Project.name.label("project_name"),
            )
            .where(Task.project_id.in_(projects))
            .join(Project, Project.id == Task.project_id)
            .order_by(Task.deadline)
        )
        tasks = await super().get_multi_paginated(query=query)

        return tasks

    async def get_not_completed_by_user(
        self, *, user: User, db_session: Optional[AsyncSession] = None
    ) -> List[ITaskWithProjectName]:
        db_session = db_session or db.session

        # get user projects
        query = select(Project.id).where(Project.users.contains(user))
        response = await db_session.execute(query)
        projects = response.scalars().all()

        # get user tasks
        query = (
            select(
                Task.id,
                Task.name,
                Task.deadline,
                Task.done,
                Task.project_id,
                Project.name.label("project_name"),
            )
            .where(Task.project_id.in_(projects))
            .where(Task.done == False)  # noqa
            .join(Project, Project.id == Task.project_id)
            .order_by(Task.deadline)
        )
        tasks = await super().get_multi_paginated(query=query)

        return tasks

    async def get_by_deadline(
        self, *, user: User, date: UTCDatetime, db_session: Optional[AsyncSession] = None
    ) -> List[ITaskWithProjectName]:
        db_session = db_session or db.session

        # get user projects
        query = select(Project.id).where(Project.users.contains(user))
        response = await db_session.execute(query)
        projects = response.scalars().all()

        date_from = datetime.fromordinal(date.toordinal())
        date_to = datetime.fromordinal(date.toordinal() + 1)

        # get user tasks
        query = (
            select(
                Task.id,
                Task.name,
                Task.deadline,
                Task.done,
                Task.project_id,
                Project.name.label("project_name"),
            )
            .where(Task.project_id.in_(projects))
            .where(and_(Task.deadline > date_from, Task.deadline < date_to))
            .join(Project, Project.id == Task.project_id)
            .order_by(Task.deadline)
        )
        tasks = await super().get_multi_paginated(query=query)

        return tasks


task = CRUDTask(Task)
