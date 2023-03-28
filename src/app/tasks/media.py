import os
from io import BytesIO

from asyncer import runnify
from celery import shared_task
from sqlmodel import select

from app.api import deps
from app.db.session import SessionLocal
from app.models.image_media_model import ImageMedia
from app.models.media_model import Media
from app.models.user_model import User
from app.schemas.media_schema import IMediaCreate
from app.utils.resize_image import IModifiedImageResponse, modify_image_resized


async def add_image(user_id: str, file_name: str, image: IModifiedImageResponse) -> None:
    async with SessionLocal() as db_session:
        # Retrieve user by ID from the database
        user = await db_session.execute(select(User).where(User.id == user_id))
        user = user.scalar_one_or_none()

        # Create a new image media object
        media = IMediaCreate(title="", description="", path=file_name)

        # Set user's image to the new image media object
        user.image = ImageMedia(
            media=Media.from_orm(media),
            height=image.height,
            width=image.width,
            file_format=image.file_format,
        )

        # Add user to database session
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)


@shared_task(name="generate_avatar_thumbnail")
def generate_avatar_thumbnail(user_id: str, file_name: str) -> None:
    # Connect to Minio client
    minio_client = deps.minio_auth()

    # Retrieve image data from Minio
    image = minio_client.get_object(file_name=file_name)
    image_bytes = BytesIO(image.read())

    # Modify the image to generate a thumbnail
    image_modified = modify_image_resized(image_bytes)

    # Get the content type of the original image
    content_type = image.getheader("content-type")

    # Generate a new file name for the thumbnail
    file_name_split = os.path.splitext(file_name)
    file_name_thumbnail = f"{file_name_split[0]}-thumbnail{file_name_split[-1]}"

    # Upload the thumbnail to Minio and get its metadata
    data_file = minio_client.put_object(
        file_name=file_name_thumbnail,
        file_data=BytesIO(image_modified.file_data),
        content_type=content_type,
    )

    # Call assynchrony function
    runnify(add_image)(user_id=user_id, file_name=data_file.file_name, image=image_modified)
