from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel


class UserBase(SQLModel):
    first_name: str
    last_name: str
    username: str = Field(nullable=True, sa_column_kwargs={"unique": True})
    email: EmailStr = Field(nullable=True, index=True, sa_column_kwargs={"unique": True})
    birthdate: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )  # birthday with timezone
    phone: Optional[str]


class User(BaseUUIDModel, UserBase, table=True):
    hashed_password: Optional[str] = Field(nullable=False, index=True)
    role_id: Optional[UUID] = Field(default=None, foreign_key="Role.id")
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
