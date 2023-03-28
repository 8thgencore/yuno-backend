from asyncer import runnify
from celery import shared_task
from loguru import logger
from sqlmodel import select

from app.db.session import SessionLocal
from app.models.project_model import Project
from app.models.task_model import Task


async def calculate(project_id: str) -> bool:
    async with SessionLocal() as db_session:
        # get the project and its associated tasks by project_id
        query = select(Project, Task).join(Task).where(Project.id == project_id)
        result = await db_session.execute(query)

        # calculate the number of completed tasks and the total number of tasks
        project = None
        task_all = 0
        task_completed = 0
        for row in result:
            if not project:
                project = row[0]
            if row[1].done:
                task_completed += 1
            task_all += 1

        # if a project was found, calculate its percentage completed and commit the changes
        if project:
            project.percent_completed = task_completed / task_all
            db_session.add(project)
            await db_session.commit()
            await db_session.refresh(project)

            return True

        return False


@shared_task(name="calculate_percent_completed_task")
def calculate_percent_completed_task(project_id: str) -> None:
    result = runnify(calculate)(project_id=project_id)
    logger.warning(f"Task calculate_percent_completed_task is {result}")
