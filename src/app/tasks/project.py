import asyncio

from celery import shared_task
from sqlmodel import and_, func, select

from app.db.session import SessionLocal
from app.models.project_model import Project
from app.models.task_model import Task


@shared_task(name="calculate_percent_completed_task")
def calculate_percent_completed_task(project_id: str):
    async def main():
        async with SessionLocal() as db_session:
            result = await db_session.execute(
                select(func.count(Task.id)).where(Task.project_id == project_id)
            )
            task_all = result.scalar()

            result = await db_session.execute(
                select(func.count(Task.id)).where(
                    and_(Task.project_id == project_id, Task.done == True)
                )
            )
            task_complited = result.scalar()

            result = await db_session.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()

            if project:
                project.percent_completed = float("{:.2f}".format(task_complited / task_all))

                db_session.add(project)
                await db_session.commit()
                await db_session.refresh(project)

    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)
