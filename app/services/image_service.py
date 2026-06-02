from app.repositories.image_repository import ImageRepository
from app.services.storage_service import StorageService
from app.utils.helpers import Helpers
from app.core.logging import logger
from app.core.exception import (
    DatabaseException,
    ImageDeletionException,
    ImageNotFoundException,
    ImageUploadException,
    InvalidImageFormatException,
    StorageServiceException,
)
import time

class ImageService:

    @Helpers().timer_method
    @staticmethod
    async def upload_image(file, metadata: dict):
        if not file.content_type or not file.content_type.startswith("image/"):
            raise InvalidImageFormatException("Uploaded file must be an image.")

        logger.info(
            "image_service.upload_image.start",
            extra={
                "user_id": metadata.get("user_id"),
                "title": metadata.get("title"),
                "tags": metadata.get("tags", []),
                "content_type": file.content_type,
            },
        )

        try:
            image_id, s3_key = await StorageService.upload_image(
                file=file,
                content_type=file.content_type
            )
        except StorageServiceException as exc:
            logger.error("image_service.upload_image.storage_failure", extra={"message": str(exc)})
            raise ImageUploadException(str(exc)) from exc
        except Exception as exc:
            logger.exception("image_service.upload_image.failure", extra={"message": str(exc)})
            raise ImageUploadException("Failed to upload the image.") from exc

        payload = {
            "image_id": image_id,
            "user_id": metadata["user_id"],
            "title": metadata["title"],
            "description": metadata.get("description"),
            "tags": metadata.get("tags", []),
            "content_type": file.content_type,
            "s3_key": s3_key,
            "created_at": Helpers().timestamp_to_iso8601(time.time())
        }

        try:
            ImageRepository.create_image(payload)
        except DatabaseException as exc:
            logger.error("image_service.upload_image.db_failure", extra={"image_id": image_id, "message": str(exc)})
            raise ImageUploadException("Failed to save image metadata.") from exc
        except Exception as exc:
            logger.exception("image_service.upload_image.db_failure", extra={"image_id": image_id, "message": str(exc)})
            raise ImageUploadException("Failed to save image metadata.") from exc

        try:
            url = StorageService.generate_presigned_url(s3_key)
        except StorageServiceException as exc:
            logger.error("image_service.upload_image.presign_failure", extra={"image_id": image_id, "message": str(exc)})
            raise ImageUploadException(str(exc)) from exc

        response = {
            "image_id": image_id,
            "image_url": url
        }
        logger.info("image_service.upload_image.success", extra={"image_id": image_id, "user_id": metadata.get("user_id")})
        return response

    @Helpers().timer_method
    @staticmethod
    def get_image(image_id: str):
        logger.info("image_service.get_image.start", extra={"image_id": image_id})
        item = ImageRepository.get_image(image_id)

        if not item:
            logger.warning("image_service.get_image.not_found", extra={"image_id": image_id})
            raise ImageNotFoundException(image_id)

        try:
            item["download_url"] = StorageService.generate_presigned_url(
                item["s3_key"]
            )
            logger.info("image_service.get_image.success", extra={"image_id": image_id})
        except StorageServiceException as exc:
            logger.error("image_service.get_image.presign_failure", extra={"image_id": image_id, "message": str(exc)})
            raise StorageServiceException(
                f"Unable to generate download URL for image {image_id}: {exc}"
            ) from exc

        return item

    @Helpers().timer_method
    @staticmethod
    def list_images(filters: dict):
        logger.info("image_service.list_images.start", extra={"filters": filters})
        try:
            items = ImageRepository.list_images(filters)
            logger.info("image_service.list_images.success", extra={"filters": filters, "count": len(items)})
            return items
        except DatabaseException:
            raise
        except Exception as exc:
            logger.exception("image_service.list_images.failure", extra={"filters": filters, "message": str(exc)})
            raise DatabaseException("Failed to list images.") from exc

    @Helpers().timer_method
    @staticmethod
    def delete_image(image_id: str):
        logger.info("image_service.delete_image.start", extra={"image_id": image_id})
        item = ImageRepository.get_image(image_id)

        if not item:
            logger.warning("image_service.delete_image.not_found", extra={"image_id": image_id})
            raise ImageNotFoundException(image_id)

        try:
            StorageService.delete_image(item["s3_key"])
            logger.info("image_service.delete_image.storage_deleted", extra={"image_id": image_id, "s3_key": item["s3_key"]})
        except StorageServiceException as exc:
            logger.error("image_service.delete_image.storage_failure", extra={"image_id": image_id, "message": str(exc)})
            raise ImageDeletionException(str(exc)) from exc
        except Exception as exc:
            logger.exception("image_service.delete_image.storage_failure", extra={"image_id": image_id, "message": str(exc)})
            raise ImageDeletionException("Failed to delete image from storage.") from exc

        try:
            ImageRepository.delete_image(image_id)
            logger.info("image_service.delete_image.db_deleted", extra={"image_id": image_id})
        except DatabaseException as exc:
            logger.error("image_service.delete_image.db_failure", extra={"image_id": image_id, "message": str(exc)})
            raise ImageDeletionException(str(exc)) from exc
        except Exception as exc:
            logger.exception("image_service.delete_image.db_failure", extra={"image_id": image_id, "message": str(exc)})
            raise ImageDeletionException("Failed to delete image metadata from database.") from exc

        logger.info("image_service.delete_image.success", extra={"image_id": image_id})
        return True
