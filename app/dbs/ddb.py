import boto3
from app.core.config import settings


dynamodb = boto3.resource(
    "dynamodb",
    region_name=settings.AWS_REGION
)

image_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)