import pytest
from httpx import AsyncClient
from app.main import app
from app.repositories.image_repository import ImageRepository


@pytest.mark.asyncio
async def test_upload_image_returns_id_and_url(aws_resources, sample_image):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        files = {
            "file": ("sample.png", sample_image, "image/png")
        }
        data = {
            "user_id": "user1",
            "title": "Test Image",
            "description": "A test image upload",
            "tags": "travel,landscape"
        }

        response = await client.post("/images", files=files, data=data)
        assert response.status_code == 200

        payload = response.json()
        assert payload["image_id"]
        assert payload["image_url"].startswith("https://")


@pytest.mark.asyncio
async def test_list_images_with_filters(aws_resources, sample_image):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        common_file = {"file": ("sample.png", sample_image, "image/png")}

        response_one = await client.post(
            "/images",
            files=common_file,
            data={
                "user_id": "user1",
                "title": "Travel Image",
                "description": "Travel photo",
                "tags": "travel"
            }
        )
        assert response_one.status_code == 200
        first_id = response_one.json()["image_id"]

        response_two = await client.post(
            "/images",
            files=common_file,
            data={
                "user_id": "user2",
                "title": "Food Image",
                "description": "Food photo",
                "tags": "food"
            }
        )
        assert response_two.status_code == 200
        second_id = response_two.json()["image_id"]

        filtered_response = await client.get("/images", params={"user_id": "user1", "tag": "travel"})
        assert filtered_response.status_code == 200
        filtered_items = filtered_response.json()
        assert len(filtered_items) == 1
        assert filtered_items[0]["image_id"] == first_id
        assert filtered_items[0]["user_id"] == "user1"

        all_response = await client.get("/images")
        assert all_response.status_code == 200
        all_items = all_response.json()
        assert {item["image_id"] for item in all_items} == {first_id, second_id}


@pytest.mark.asyncio
async def test_get_image_returns_details(aws_resources, sample_image):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        files = {
            "file": ("sample.png", sample_image, "image/png")
        }
        data = {
            "user_id": "user1",
            "title": "Test Image",
            "description": "A test image upload",
            "tags": "travel,landscape"
        }

        upload_response = await client.post("/images", files=files, data=data)
        image_id = upload_response.json()["image_id"]

        get_response = await client.get(f"/images/{image_id}")
        assert get_response.status_code == 200

        item = get_response.json()
        assert item["image_id"] == image_id
        assert item["user_id"] == "user1"
        assert item["title"] == "Test Image"
        assert item["description"] == "A test image upload"
        assert item["tags"] == ["travel", "landscape"]
        assert item["download_url"].startswith("https://")


@pytest.mark.asyncio
async def test_delete_image_removes_item(aws_resources, sample_image):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        files = {
            "file": ("sample.png", sample_image, "image/png")
        }
        data = {
            "user_id": "user1",
            "title": "Delete Test",
            "description": "This image will be deleted",
            "tags": "archive"
        }

        upload_response = await client.post("/images", files=files, data=data)
        image_id = upload_response.json()["image_id"]

        delete_response = await client.delete(f"/images/{image_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Image deleted successfully"

        get_response = await client.get(f"/images/{image_id}")
        assert get_response.status_code == 404

        list_response = await client.get("/images")
        assert list_response.status_code == 200
        assert all(item["image_id"] != image_id for item in list_response.json())


@pytest.mark.asyncio
async def test_get_missing_image_returns_404(aws_resources):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/images/nonexistent-id")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_missing_image_returns_404(aws_resources):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.delete("/images/nonexistent-id")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_images_empty_filters(aws_resources):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/images")
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_get_upload_url_returns_presigned_url(aws_resources):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/images/get_upload_url")
        assert response.status_code == 200

        payload = response.json()
        assert "image_id" in payload
        assert "key" in payload
        assert "upload_url" in payload

        # Validate format
        assert payload["image_id"]  # UUID should not be empty
        assert payload["key"].startswith("images/")  # Key should follow the pattern
        assert payload["upload_url"].startswith("https://")  # Presigned URL should be HTTPS
        assert "s3" in payload["upload_url"].lower()  # Should contain S3 reference


@pytest.mark.asyncio
async def test_get_upload_url_returns_valid_image_id_key_pair(aws_resources):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/images/get_upload_url")
        assert response.status_code == 200

        payload = response.json()
        # The key should contain the image_id
        assert payload["image_id"] in payload["key"]
        assert payload["key"] == f"images/{payload['image_id']}"


@pytest.mark.asyncio
async def test_get_upload_url_multiple_calls_generate_unique_ids(aws_resources):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response_one = await client.get("/images/get_upload_url")
        assert response_one.status_code == 200
        payload_one = response_one.json()

        response_two = await client.get("/images/get_upload_url")
        assert response_two.status_code == 200
        payload_two = response_two.json()

        # Each call should generate a unique image_id and upload_url
        assert payload_one["image_id"] != payload_two["image_id"]
        assert payload_one["upload_url"] != payload_two["upload_url"]


@pytest.mark.asyncio
async def test_get_upload_url_presigned_url_has_expiration(aws_resources):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/images/get_upload_url")
        assert response.status_code == 200

        payload = response.json()
        upload_url = payload["upload_url"]
        
        # Presigned URLs should contain X-Amz-Expires parameter (3600 seconds)
        assert "X-Amz-Expires" in upload_url
        assert "3600" in upload_url


@pytest.mark.asyncio
async def test_get_upload_url_creates_pending_metadata(aws_resources):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get(
            "/images/get_upload_url",
            params={
                "user_id": "pending-user",
                "title": "Pending Image",
                "description": "Metadata should be stored",
                "tags": "pending,upload",
                "content_type": "image/png"
            }
        )
        assert response.status_code == 200

        payload = response.json()
        image_id = payload["image_id"]
        item = ImageRepository.get_image(image_id)

        assert item is not None
        assert item["image_id"] == image_id
        assert item["status"] == "PENDING"
        assert item["user_id"] == "pending-user"
        assert item["title"] == "Pending Image"
        assert item["description"] == "Metadata should be stored"
        assert item["tags"] == ["pending", "upload"]
        assert item["content_type"] == "image/png"
        assert item["s3_key"] == payload["key"]


def test_s3_event_handler_updates_pending_upload(aws_resources):
    from app.core.config import settings
    from app.s3_event_handler import handler as s3_event_handler

    image_id = "pending-event-id"
    ImageRepository.create_image({
        "image_id": image_id,
        "s3_key": f"images/{image_id}",
        "status": "PENDING"
    })

    event = {
        "Records": [
            {
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {"name": settings.S3_BUCKET_NAME},
                    "object": {"key": f"images/{image_id}"},
                },
            }
        ]
    }

    result = s3_event_handler(event, None)
    assert result["status"] == "processed"
    assert result["records"] == 1

    item = ImageRepository.get_image(image_id)
    assert item is not None
    assert item["status"] == "UPLOADED"
    assert item["uploaded_at"]
