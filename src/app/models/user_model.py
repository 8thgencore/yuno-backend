from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import BigInteger, Column, DateTime, Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel


class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr = Field(nullable=True, index=True, sa_column_kwargs={"unique": True})
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    birthdate: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )  # birthday with timezone
    role_id: Optional[UUID] = Field(default=None, foreign_key="Role.id")
    phone: Optional[str]


class User(BaseUUIDModel, UserBase, table=True):
    hashed_password: Optional[str] = Field(nullable=False, index=True)
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )
