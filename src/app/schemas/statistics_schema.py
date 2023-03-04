from pydantic import BaseModel


class StatisticsRead(BaseModel):
    projects_count: int
    missing_count: int
    ongoing_count: int
    completed_count: int
