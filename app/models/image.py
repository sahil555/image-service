from pydantic import BaseModel
from typing import Optional


class ImageMetadata(BaseModel):
    image_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    tags: list[str] = []
    content_type: str
    s3_key: str
    created_at: str