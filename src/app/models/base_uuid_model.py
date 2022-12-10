from datetime import datetime
from typing import Optional

from sqlalchemy.orm import declared_attr
from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel

from app.utils.uuid6 import UUID, uuid7

# id: implements proposal uuid7 draft4


class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__


class BaseUUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: Optional[datetime] = Field(default=datetime.now())
    created_at: Optional[datetime] = Field(default=datetime.now())
