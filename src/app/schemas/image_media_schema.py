from typing import Optional

from app.models.media_model import ImageMediaBase, IMediaRead
from app.utils.partial import optional


# Image Media
class IImageMediaCreate(ImageMediaBase):
    pass


# All these fields are optional
@optional
class IImageMediaUpdate(ImageMediaBase):
    pass


class IImageMediaRead(ImageMediaBase):
    media: Optional[IMediaRead]
