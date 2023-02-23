import asyncio
import os
from io import BytesIO

from celery import shared_task
from sqlmodel import select

from app.api import deps
from app.db.session import SessionLocal
from app.models.image_media_model import ImageMedia
from app.models.media_model import Media
from app.models.user_model import User
from app.schemas.media_schema import IMediaCreate
from app.utils.resize_image import modify_image_resized


@shared_task(name="generate_avatar_thumbnail")
def generate_avatar_thumbnail(user_id: str, file_name: str):
    minio_client = deps.minio_auth()

    image = minio_client.get_object(file_name=file_name)
    image_bytes = BytesIO(image.read())
    image_modified = modify_image_resized(image_bytes)

    content_type = image.getheader("content-type")

    file_name_split = os.path.splitext(file_name)
    file_name_thumbnail = f"{file_name_split[0]}-thumbnail{file_name_split[-1]}"

    data_file = minio_client.put_object(
        file_name=file_name_thumbnail,
        file_data=BytesIO(image_modified.file_data),
        content_type=content_type,
    )

    # Add to Database
    async def main():
        async with SessionLocal() as db_session:
            user = await db_session.execute(select(User).where(User.id == user_id))
            user = user.scalar_one_or_none()

            media = IMediaCreate(title="", description="", path=data_file.file_name)

            user.image = ImageMedia(
                media=Media.from_orm(media),
                height=image_modified.height,
                width=image_modified.width,
                file_format=image_modified.file_format,
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)

    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)
