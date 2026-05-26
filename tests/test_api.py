import pytest
from httpx import AsyncClient
from app.main import app


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
