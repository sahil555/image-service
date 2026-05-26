# Image backend service

## Overview & Intro

I designed the service using a layered architecture with separation between API, service, repository, and infrastructure layers. Images are stored in S3 while metadata is persisted in DynamoDB for scalability and low operational overhead. 

The application is stateless and containerized using Docker, making it deployable across Lambda, ECS, and Kubernetes. 

Presigned URLs are used to avoid routing large image payloads through backend servers, significantly improving scalability and reducing compute cost.

# High-Level Architecture

                ┌──────────────────┐
                │   API Gateway    │
                └────────┬─────────┘
                         │
                  Lambda / ECS 
                         │
                ┌────────▼─────────┐
                │     FastAPI      │
                └────────┬─────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                │
 ┌───────▼────────┐              ┌────────▼────────┐
 │       S3       │              │    DynamoDB     │
 │ Image Storage  │              │ Metadata Store  │
 └────────────────┘              └─────────────────┘

# This service is an Instagram-style image platform where:

User uploads image + metadata
Image gets stored in S3
Metadata gets stored in DynamoDB
APIs serve metadata + secure download URLs
Service scales horizontally using Lambda/ECS

# API 
POST /images
GET /images?user_id=u1&tag=travel
GET /images/{image_id}
DELETE /images/{image_id}

# Step by Step process execution of APIs

1. POST /images

User uploads image
        │
        ▼
FastAPI route receives multipart file
        │
        ▼
ImageService.upload_image()
        │
        ├── StorageService uploads image to S3
        │
        ├── Generates unique image_id
        │
        ├── Metadata prepared
        │
        ▼
ImageRepository saves metadata in DynamoDB
        │
        ▼
Presigned URL generated
        │
        ▼
Response returned

2. GET /images?user_id=u1&tag=travel

FastAPI Route
      │
      ▼
ImageService.list_images()
      │
      ▼
ImageRepository.list_images()
      │
      ▼
DynamoDB query/scan
      │
      ▼
Filtered response

3. 

Fetch metadata from DynamoDB
        │
        ▼
Generate temporary S3 presigned URL
        │
        ▼
Return secure downloadable URL

4. DELETE /images/{image_id}

Fetch metadata
     │
     ├── Delete from S3
     │
     └── Delete from DynamoDB

## lambda_handler

Purpose : Converts FastAPI ASGI app into AWS Lambda-compatible handler.

AWS Lambda does not understand FastAPI directly.

Mangum acts as adapter:
    API Gateway Event
            ↓
        Mangum
            ↓
        FastAPI

## Service Layer

Handles business workflows.
    - Upload image
    - Build metadata
    - Save metadata
    - Generate URL
    - Reusable

storage_service
    - Upload file
    - Delete file
    - Generate presigned URL

image_repository
    - put_item
    - get_item
    - delete_item

config
    - Centralized environment configuration.
    - Environment-driven config is mandatory for production.

logging
    - Structured JSON logging.
    - Very important at scale.
    - Easily utilizes from Observability tools like OpenTelemetry


## Quick Start (local)

- Create and activate a virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Install dependencies:

```bash
python -m pip install -r requirements.txt
```

- Run the app:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Tests

- Run tests locally:

```bash
pytest -q
```

- Run tests inside the container (image built by docker-compose):

```bash
docker compose -f docker-compose.yml up --build
docker exec -w /app image-service pytest -q
```

## Docker

- Notes:
  - The Docker build context is set to the project root in `docker-compose.yml`.
  - The `deployment/docker/Dockerfile` base image was changed to `python:3.14-slim` to match development dependency wheels.
  - The final stage installs `requirements.txt` so CLI entrypoints like `uvicorn` are available.

- To build and run with compose:

```bash
docker compose -f docker-compose.yml up -d --build
```

## Environment

- Configure the following environment variables (see `.env` for defaults):
  - `AWS_REGION`
  - `S3_BUCKET_NAME`
  - `DYNAMODB_TABLE_NAME`

## Serverless lambda details

