from datetime import datetime
from app.repositories.image_repository import ImageRepository
from app.services.storage_service import StorageService


class ImageService:

    @staticmethod
    async def upload_image(file, metadata: dict):

        image_id, s3_key = await StorageService.upload_image(
            file=file,
            content_type=file.content_type
        )

        payload = {
            "image_id": image_id,
            "user_id": metadata["user_id"],
            "title": metadata["title"],
            "description": metadata.get("description"),
            "tags": metadata.get("tags", []),
            "content_type": file.content_type,
            "s3_key": s3_key,
            "created_at": datetime.utcnow().isoformat()
        }

        ImageRepository.create_image(payload)

        url = StorageService.generate_presigned_url(s3_key)

        return {
            "image_id": image_id,
            "image_url": url
        }

    @staticmethod
    def get_image(image_id: str):
        item = ImageRepository.get_image(image_id)

        if not item:
            return None

        item["download_url"] = StorageService.generate_presigned_url(
            item["s3_key"]
        )

        return item

    @staticmethod
    def list_images(filters: dict):
        return ImageRepository.list_images(filters)
    
    @staticmethod
    def delete_image(image_id: str):
        item = ImageRepository.get_image(image_id)

        if not item:
            return False

        StorageService.delete_image(item["s3_key"])
        ImageRepository.delete_image(image_id)

        return True