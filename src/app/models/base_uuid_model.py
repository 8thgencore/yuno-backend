from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict
from sqlalchemy.orm import declared_attr
from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel

from app.utils.uuid6 import uuid7

# id: implements proposal uuid7 draft4


class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__


class BaseUUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
    created_at: datetime | None = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(arbitrary_types_allowed=True)


# class UTCDatetime(datetime):
#     """parse a datetime and convert in into UTC format"""

#     @classmethod
#     def __get_pydantic_core_schema__(cls) -> Any:
#         yield cls.validate

#     # TODO:
#     # @classmethod
#     # def validate(cls, v: Any) -> datetime:
#     #     return datetime.fromtimestamp(parse_datetime(v).timestamp())
