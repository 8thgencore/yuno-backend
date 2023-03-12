from io import BytesIO
from typing import Any

from PIL import Image
from pydantic import BaseModel


class IModifiedImageResponse(BaseModel):
    width: int
    height: int
    file_format: str
    file_data: Any


def crop_center(pil_img, crop_width, crop_height) -> Any:
    img_width, img_height = pil_img.size
    return pil_img.crop(
        (
            (img_width - crop_width) // 2,
            (img_height - crop_height) // 2,
            (img_width + crop_width) // 2,
            (img_height + crop_height) // 2,
        )
    )


def crop_max_square(pil_img) -> Any:
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def modify_image(image: BytesIO) -> IModifiedImageResponse:
    pil_image = Image.open(image)
    file_format = pil_image.format

    in_mem_file = BytesIO()

    # format here would be something like "JPEG". See below link for more info.
    pil_image.save(in_mem_file, format=file_format)

    return IModifiedImageResponse(
        width=pil_image.width,
        height=pil_image.height,
        file_format=file_format,
        file_data=in_mem_file.getvalue(),
    )


def modify_image_resized(image: BytesIO) -> IModifiedImageResponse:
    size = (256, 256)

    pil_image = Image.open(image)
    file_format = pil_image.format
    pil_image = crop_max_square(pil_image).resize(size, Image.Resampling.LANCZOS)
    in_mem_file = BytesIO()

    # format here would be something like "JPEG". See below link for more info.
    pil_image.save(in_mem_file, format=file_format)

    return IModifiedImageResponse(
        width=pil_image.width,
        height=pil_image.height,
        file_format=file_format,
        file_data=in_mem_file.getvalue(),
    )
