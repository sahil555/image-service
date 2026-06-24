import boto3
from typing import Any
from app.core.config import settings


def get_dynamodb_resource() -> Any:
    resource_kwargs = {"region_name": settings.AWS_REGION}

    if settings.USE_LOCALSTACK:
        resource_kwargs["endpoint_url"] = settings.AWS_ENDPOINT_URL or "http://localstack:4566"
    elif settings.AWS_ENDPOINT_URL:
        resource_kwargs["endpoint_url"] = settings.AWS_ENDPOINT_URL

    return boto3.resource("dynamodb", **resource_kwargs)


def get_image_table():
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
