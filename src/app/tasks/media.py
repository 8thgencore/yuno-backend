import os
from io import BytesIO

from celery import shared_task

from app.api import deps
from app.schemas.media_schema import IMediaCreate
from app.utils.resize_image import modify_image_resized


@shared_task(name="generate_avatar_thumbnail")
def generate_avatar_thumbnail(file_name: str):
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
    IMediaCreate(title="", description="", path=data_file.file_name)

    # print(media)
    # user = await crud.user.update_photo(
    #     user=current_user,
    #     image=media,
    #     heigth=image_modified.height,
    #     width=image_modified.width,
    #     file_format=image_modified.file_format,
    # )

    # with db_context() as session:
    #     member = session.query(Member).get(member_pk)

    #     full_path = os.path.join(settings.UPLOADS_DEFAULT_DEST, member.avatar)

    #     thumbnail_path = f"{member.id}-thumbnail.jpg"
    #     thumbnail_full_path = os.path.join(settings.UPLOADS_DEFAULT_DEST, thumbnail_path)

    #     im = Image.open(full_path)
    #     size = (120, 120)
    #     im.thumbnail(size)
    #     im.save(thumbnail_full_path, "JPEG")

    #     member.avatar_thumbnail = thumbnail_path
    #     session.add(member)
    #     session.commit()
