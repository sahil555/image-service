from pydantic import BaseModel
from typing import Optional


class UploadImageResponse(BaseModel):
    image_id: str
    image_url: str


class ImageFilterSchema(BaseModel):
    user_id: Optional[str] = None
    tag: Optional[str] = None