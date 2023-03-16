from typing import Any

from pydantic.networks import EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.crud.base_crud import CRUDBase
from app.models.image_media_model import ImageMedia
from app.models.media_model import Media
from app.models.user_model import User
from app.schemas.media_schema import IMediaCreate
from app.schemas.user_schema import IUserCreate, IUserUpdate


class CRUDUser(CRUDBase[User, IUserCreate, IUserUpdate]):
    async def get_by_email(
        self, *, email: str, db_session: AsyncSession | None = None
    ) -> User | None:
        db_session = db_session or super().get_db().session
        user = await db_session.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()

    async def get_by_username(
        self, *, username: str, db_session: AsyncSession | None = None
    ) -> User | None:
        db_session = db_session or super().get_db().session
        user = await db_session.execute(select(User).where(User.username == username))
        return user.scalar_one_or_none()

    async def create_with_role(
        self, *, obj_in: IUserCreate, db_session: AsyncSession | None = None
    ) -> User:
        db_session = db_session or super().get_db().session
        db_obj = User.from_orm(obj_in)
        db_obj.hashed_password = get_password_hash(obj_in.password)

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def update_is_active(
        self, *, db_obj: list[User], obj_in: int | str | dict[str, Any]
    ) -> User | None:
        db_session = super().get_db().session

        response = None
        for x in db_obj:
            x.is_active = obj_in.is_active
            db_session.add(x)
            await db_session.commit()
            await db_session.refresh(x)
            response.append(x)
        return response

    async def authenticate(self, *, email: EmailStr, password: str) -> User | None:
        user = await self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_photo(
        self,
        *,
        user: User,
        image: IMediaCreate,
        heigth: int,
        width: int,
        file_format: str,
    ) -> User:
        db_session = super().get_db().session

        user.image = ImageMedia(
            media=Media.from_orm(image),
            height=heigth,
            width=width,
            file_format=file_format,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user


user = CRUDUser(User)
