from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.core.logging import logger
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


@router.get("/get_upload_url")
def get_upload_url(
    user_id: str = "",
    title: str = "",
    description: str = "",
    tags: str = "",
    content_type: str = "image/png"
):
    metadata = {
        "user_id": user_id,
        "title": title,
        "description": description or None,
        "tags": tags.split(",") if tags else [],
        "content_type": content_type,
    }

    logger.info("get_upload_url.request", extra=metadata)
    try:
        response = ImageService.generate_upload_url(**metadata)
        logger.info("get_upload_url.success", extra={"image_id": response["image_id"], "key": response["key"]})
        return response
    except (InvalidImageFormatException, ValidationException) as exc:
        logger.warning("get_upload_url.validation_failure", extra={"error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc))
    except (ImageUploadException, StorageServiceException, DatabaseException) as exc:
        logger.error("get_upload_url.failure", extra={"error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("get_upload_url.unexpected_error", extra={"error": str(exc)})
        raise HTTPException(status_code=500, detail="Unexpected error while generating upload URL.") from exc


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

    logger.info("upload_image.request", extra={"user_id": user_id, "title": title, "tags": metadata["tags"]})
    try:
        response = await ImageService.upload_image(file, metadata)
        logger.info("upload_image.success", extra={"user_id": user_id, "image_id": response["image_id"]})
        return response
    except (InvalidImageFormatException, ValidationException) as exc:
        logger.warning("upload_image.validation_failure", extra={"user_id": user_id, "error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc))
    except (ImageUploadException, StorageServiceException, DatabaseException) as exc:
        logger.error("upload_image.failure", extra={"user_id": user_id, "error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("upload_image.unexpected_error", extra={"user_id": user_id, "error": str(exc)})
        raise HTTPException(status_code=500, detail="Unexpected error during image upload.") from exc


@router.get("")
def list_images(
    user_id: str = "",
    tag: str = ""
):
    logger.info("list_images.request", extra={"user_id": user_id, "tag": tag})
    try:
        items = ImageService.list_images({
            "user_id": user_id,
            "tag": tag
        })
        logger.info("list_images.success", extra={"user_id": user_id, "tag": tag, "count": len(items)})
        return items
    except ValidationException as exc:
        logger.warning("list_images.validation_failure", extra={"user_id": user_id, "tag": tag, "error": str(exc)})
        raise HTTPException(status_code=422, detail=str(exc))
    except DatabaseException as exc:
        logger.error("list_images.failure", extra={"user_id": user_id, "tag": tag, "error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("list_images.unexpected_error", extra={"user_id": user_id, "tag": tag, "error": str(exc)})
        raise HTTPException(status_code=500, detail="Unexpected error during image listing.") from exc


@router.get("/{image_id}")
def get_image(image_id: str):
    logger.info("get_image.request", extra={"image_id": image_id})
    try:
        item = ImageService.get_image(image_id)
        logger.info("get_image.success", extra={"image_id": image_id})
        return item
    except ImageNotFoundException as exc:
        logger.warning("get_image.not_found", extra={"image_id": image_id, "error": str(exc)})
        raise HTTPException(status_code=404, detail=str(exc))
    except StorageServiceException as exc:
        logger.error("get_image.failure", extra={"image_id": image_id, "error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("get_image.unexpected_error", extra={"image_id": image_id, "error": str(exc)})
        raise HTTPException(status_code=500, detail="Unexpected error while fetching image.") from exc


@router.delete("/{image_id}")
def delete_image(image_id: str):
    logger.info("delete_image.request", extra={"image_id": image_id})
    try:
        ImageService.delete_image(image_id)
        logger.info("delete_image.success", extra={"image_id": image_id})
        return {"message": "Image deleted successfully"}
    except ImageNotFoundException as exc:
        logger.warning("delete_image.not_found", extra={"image_id": image_id, "error": str(exc)})
        raise HTTPException(status_code=404, detail=str(exc))
    except ImageDeletionException as exc:
        logger.error("delete_image.failure", extra={"image_id": image_id, "error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("delete_image.unexpected_error", extra={"image_id": image_id, "error": str(exc)})
        raise HTTPException(status_code=500, detail="Unexpected error while deleting image.") from exc
