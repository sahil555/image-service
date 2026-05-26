import boto3
from uuid import uuid4
from app.core.config import settings


s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION
)


class StorageService:

    @staticmethod
    async def upload_image(file, content_type: str):
        image_id = str(uuid4())
        key = f"images/{image_id}"

        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET_NAME,
            key,
            ExtraArgs={
                "ContentType": content_type
            }
        )
        return image_id, key

    @staticmethod
    def generate_presigned_url(key: str):
        return s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': key,
            },
            ExpiresIn=3600,
        )

    @staticmethod
    def delete_image(key: str):
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key
        )