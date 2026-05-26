from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.image_service import ImageService
from app.core.exception import (
    DatabaseException,
    ImageDeletionException,
    ImageNotFoundException,
    ImageUploadException,
    InvalidImageFormatException,
    StorageServiceException,
    ValidationException,
)

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

    try:
        return await ImageService.upload_image(file, metadata)
    except (InvalidImageFormatException, ValidationException) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except (ImageUploadException, StorageServiceException, DatabaseException) as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected error during image upload.") from exc


@router.get("")
def list_images(
    user_id: str = "",
    tag: str = ""
):
    try:
        return ImageService.list_images({
            "user_id": user_id,
            "tag": tag
        })
    except ValidationException as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except DatabaseException as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected error during image listing.") from exc


@router.get("/{image_id}")
def get_image(image_id: str):
    try:
        return ImageService.get_image(image_id)
    except ImageNotFoundException as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except StorageServiceException as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected error while fetching image.") from exc


@router.delete("/{image_id}")
def delete_image(image_id: str):
    try:
        ImageService.delete_image(image_id)
        return {"message": "Image deleted successfully"}
    except ImageNotFoundException as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ImageDeletionException as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected error while deleting image.") from exc
