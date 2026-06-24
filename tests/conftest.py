"""test fixtures for the image service"""
import os

import boto3
import pytest
from moto import mock_aws
from PIL import Image
from io import BytesIO
 
from app.core.config import settings

@pytest.fixture
def sample_image():
    """Creates a sample image for testing."""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = settings.AWS_REGION
    yield


@pytest.fixture
def aws_resources(aws_credentials):
    with mock_aws():
        s3 = boto3.client("s3", region_name=settings.AWS_REGION)
        if settings.AWS_REGION == "us-east-1":
            s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)
        else:
            s3.create_bucket(
                Bucket=settings.S3_BUCKET_NAME,
                CreateBucketConfiguration={"LocationConstraint": settings.AWS_REGION}
            )

        dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
        dynamodb.create_table(
            TableName=settings.DYNAMODB_TABLE_NAME,
            KeySchema=[{"AttributeName": "image_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "image_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        yield


@pytest.fixture
def localstack_resources(aws_credentials):
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566")
    settings.USE_LOCALSTACK = True
    settings.AWS_ENDPOINT_URL = endpoint_url

    s3 = boto3.client("s3", region_name=settings.AWS_REGION, endpoint_url=endpoint_url)
    if settings.AWS_REGION == "us-east-1":
        s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)
    else:
        s3.create_bucket(
            Bucket=settings.S3_BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": settings.AWS_REGION}
        )

    dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION, endpoint_url=endpoint_url)
    dynamodb.create_table(
        TableName=settings.DYNAMODB_TABLE_NAME,
        KeySchema=[{"AttributeName": "image_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "image_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )

    yield

    settings.USE_LOCALSTACK = False
    settings.AWS_ENDPOINT_URL = None

@pytest.fixture
def sample_image_path(tmp_path):
    """Creates a sample image file for testing."""
    img = Image.new('RGB', (100, 100), color='blue')
    img_path = tmp_path / "sample_image.png"
    img.save(img_path)
    return img_path

@pytest.fixture
def sample_image_url():
    """Returns a sample image URL for testing."""
    return "https://via.placeholder.com/150"

@pytest.fixture
def sample_image_bytes(sample_image):
    """Returns the bytes of the sample image for testing."""
    return sample_image.getvalue()

@pytest.fixture
def sample_image_pil(sample_image):
    """Returns a PIL Image object for the sample image."""
    return Image.open(sample_image) 

@pytest.fixture
def sample_image_metadata(sample_image_pil):
    """Returns metadata of the sample image for testing."""
    return {
        "format": sample_image_pil.format,
        "mode": sample_image_pil.mode,
        "size": sample_image_pil.size
    }

@pytest.fixture
def sample_image_bytes_io(sample_image):
    """Returns a BytesIO object for the sample image."""
    return BytesIO(sample_image.getvalue()) 

@pytest.fixture
def sample_image_file(sample_image_path):
    """Returns a file-like object for the sample image."""
    return open(sample_image_path, 'rb')    

@pytest.fixture
def sample_image_url_response(sample_image_url):
    """Mocks a response for the sample image URL."""
    class MockResponse:
        def __init__(self, content):
            self.content = content
            self.status_code = 200

        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP Error")

    # Create a sample image in memory and return its bytes as the response content
    img = Image.new('RGB', (150, 150), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return MockResponse(img_bytes.getvalue())

@pytest.fixture
def sample_image_processing_result():
    """Returns a sample result of image processing for testing."""
    return {
        "processed_image": "processed_image.png",
        "metadata": {
            "format": "PNG",
            "mode": "RGB",
            "size": (100, 100)
        }
    }   

@pytest.fixture
def sample_image_processing_error():    
    """Returns a sample error message for image processing failure."""
    return "Error processing image: Invalid format" 

@pytest.fixture
def sample_image_processing_exception():
    """Returns a sample exception for image processing failure."""
    class SampleProcessingException(Exception):
        pass

    return SampleProcessingException("Sample processing error")

@pytest.fixture
def sample_image_processing_warning():
    """Returns a sample warning message for image processing."""
    return "Warning: Image size is larger than recommended" 

@pytest.fixture
def sample_image_processing_log():
    """Returns a sample log message for image processing."""
    return "Processing image: sample_image.png"

@pytest.fixture
def sample_image_processing_metrics():
    """Returns sample metrics for image processing."""
    return {
        "processing_time": 0.5,
        "memory_usage": 50.0,
        "cpu_usage": 20.0
    }

@pytest.fixture
def sample_image_processing_config():
    """Returns a sample configuration for image processing."""
    return {
        "resize": (100, 100),
        "format": "PNG",
        "quality": 90
    }