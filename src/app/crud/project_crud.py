from typing import Optional

from fastapi_async_sqlalchemy import db
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models import Project
from app.models.user_model import User
from app.schemas.project_schema import IProjectCreate, IProjectUpdate


class CRUDProject(CRUDBase[Project, IProjectCreate, IProjectUpdate]):
    async def create(
        self, *, obj_in: IProjectCreate, user: User, db_session: Optional[AsyncSession] = None
    ) -> Project:
        db_session = db_session or db.session

        db_obj = Project.from_orm(obj_in)
        db_obj.created_by_id = user.id

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj


project = CRUDProject(Project)
