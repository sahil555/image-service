from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.image_service import ImageService

router = APIRouter(prefix="/images", tags=["images"])


@router.post("")
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    tags: str = Form(None)
):

    metadata = {
        "user_id": user_id,
        "title": title,
        "description": description,
        "tags": tags.split(",") if tags else []
    }
    return await ImageService.upload_image(file, metadata)


@router.get("")
def list_images(
    user_id: str = None,
    tag: str = None
):

    return ImageService.list_images({
        "user_id": user_id,
        "tag": tag
    })


@router.get("/{image_id}")
def get_image(image_id: str):

    item = ImageService.get_image(image_id)

    if not item:
        raise HTTPException(404, "Image not found")

    return item

@router.delete("/{image_id}")
def delete_image(image_id: str):

    deleted = ImageService.delete_image(image_id)

    if not deleted:
        raise HTTPException(404, "Image not found")

    return {
        "message": "Image deleted successfully"
    }