import boto3
from uuid import uuid4
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.exception import StorageServiceException
from app.core.logging import logger
from app.utils.helpers import Helpers


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION
    )


class StorageService:

    @Helpers().timer_method
    @staticmethod
    async def upload_image(file, content_type: str):
        image_id = str(uuid4())
        key = f"images/{image_id}"
        logger.info("storage.upload_image.start", extra={"image_id": image_id, "content_type": content_type})

        try:
            s3_client = get_s3_client()
            s3_client.upload_fileobj(
                file.file,
                settings.S3_BUCKET_NAME,
                key,
                ExtraArgs={
                    "ContentType": content_type
                }
            )
            logger.info("storage.upload_image.complete", extra={"image_id": image_id, "s3_key": key})
        except ClientError as exc:
            logger.exception("storage.upload_image.failure", extra={"image_id": image_id, "error": str(exc)})
            raise StorageServiceException(f"Failed to upload image to S3: {exc}") from exc
        except Exception as exc:
            logger.exception("storage.upload_image.failure", extra={"image_id": image_id, "error": str(exc)})
            raise StorageServiceException("Unexpected storage error while uploading.") from exc

        return image_id, key

    @Helpers().timer_method
    @staticmethod
    def generate_presigned_url(key: str):
        logger.info("storage.generate_presigned_url.start", extra={"s3_key": key})
        try:
            s3_client = get_s3_client()
            url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': settings.S3_BUCKET_NAME,
                    'Key': key,
                },
                ExpiresIn=3600,
            )
            logger.info("storage.generate_presigned_url.success", extra={"s3_key": key})
            return url
        except ClientError as exc:
            logger.exception("storage.generate_presigned_url.failure", extra={"s3_key": key, "error": str(exc)})
            raise StorageServiceException(f"Failed to generate presigned URL: {exc}") from exc
        except Exception as exc:
            logger.exception("storage.generate_presigned_url.failure", extra={"s3_key": key, "error": str(exc)})
            raise StorageServiceException("Unexpected storage error while generating presigned URL.") from exc

    @Helpers().timer_method
    @staticmethod
    def generate_presigned_upload_url(content_type: str = "image/png"):
        """Generate a presigned PUT URL and return (image_id, key, upload_url)."""
        image_id = str(uuid4())
        key = f"images/{image_id}"
        params = {
            'Bucket': settings.S3_BUCKET_NAME,
            'Key': key,
        }
        if content_type:
            params['ContentType'] = content_type

        logger.info("storage.generate_presigned_upload_url.start", extra={"image_id": image_id, "s3_key": key, "content_type": content_type})
        try:
            s3_client = get_s3_client()
            upload_url = s3_client.generate_presigned_url(
                ClientMethod='put_object',
                Params=params,
                ExpiresIn=3600,
            )
            logger.info("storage.generate_presigned_upload_url.success", extra={"image_id": image_id, "s3_key": key})
            return image_id, key, upload_url
        except ClientError as exc:
            logger.exception("storage.generate_presigned_upload_url.failure", extra={"image_id": image_id, "error": str(exc)})
            raise StorageServiceException(f"Failed to generate presigned upload URL: {exc}") from exc
        except Exception as exc:
            logger.exception("storage.generate_presigned_upload_url.failure", extra={"image_id": image_id, "error": str(exc)})
            raise StorageServiceException("Unexpected storage error while generating presigned upload URL.") from exc

    @Helpers().timer_method
    @staticmethod
    def delete_image(key: str):
        logger.info("storage.delete_image.start", extra={"s3_key": key})
        try:
            s3_client = get_s3_client()
            s3_client.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key
            )
            logger.info("storage.delete_image.success", extra={"s3_key": key})
        except ClientError as exc:
            logger.exception("storage.delete_image.failure", extra={"s3_key": key, "error": str(exc)})
            raise StorageServiceException(f"Failed to delete image from S3: {exc}") from exc
        except Exception as exc:
            logger.exception("storage.delete_image.failure", extra={"s3_key": key, "error": str(exc)})
            raise StorageServiceException("Unexpected storage error while deleting image.") from exc
