from app.repositories.image_repository import ImageRepository
from app.services.storage_service import StorageService
from app.utils.helpers import Helpers
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

        try:
            image_id, s3_key = await StorageService.upload_image(
                file=file,
                content_type=file.content_type
            )
        except StorageServiceException as exc:
            raise ImageUploadException(str(exc)) from exc
        except Exception as exc:
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
            raise ImageUploadException("Failed to save image metadata.") from exc
        except Exception as exc:
            raise ImageUploadException("Failed to save image metadata.") from exc

        try:
            url = StorageService.generate_presigned_url(s3_key)
        except StorageServiceException as exc:
            raise ImageUploadException(str(exc)) from exc

        return {
            "image_id": image_id,
            "image_url": url
        }

    @Helpers().timer_method
    @staticmethod
    def get_image(image_id: str):
        item = ImageRepository.get_image(image_id)

        if not item:
            raise ImageNotFoundException(image_id)

        try:
            item["download_url"] = StorageService.generate_presigned_url(
                item["s3_key"]
            )
        except StorageServiceException as exc:
            raise StorageServiceException(
                f"Unable to generate download URL for image {image_id}: {exc}"
            ) from exc

        return item

    @Helpers().timer_method
    @staticmethod
    def list_images(filters: dict):
        try:
            return ImageRepository.list_images(filters)
        except DatabaseException:
            raise
        except Exception as exc:
            raise DatabaseException("Failed to list images.") from exc

    @Helpers().timer_method
    @staticmethod
    def delete_image(image_id: str):
        item = ImageRepository.get_image(image_id)

        if not item:
            raise ImageNotFoundException(image_id)

        try:
            StorageService.delete_image(item["s3_key"])
        except StorageServiceException as exc:
            raise ImageDeletionException(str(exc)) from exc
        except Exception as exc:
            raise ImageDeletionException("Failed to delete image from storage.") from exc

        try:
            ImageRepository.delete_image(image_id)
        except DatabaseException as exc:
            raise ImageDeletionException(str(exc)) from exc
        except Exception as exc:
            raise ImageDeletionException("Failed to delete image metadata from database.") from exc

        return True
