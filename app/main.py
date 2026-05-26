from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.images import router as image_router
from app.core.exception import (
    DatabaseException,
    ImageDeletionException,
    ImageNotFoundException,
    ImageUploadException,
    InvalidImageFormatException,
    StorageServiceException,
    ValidationException,
)


def create_error_response(status_code: int, message: str):
    return JSONResponse(status_code=status_code, content={"detail": message})


app = FastAPI(
    title="Image Service API",
    version="1.0.0"
)

app.include_router(image_router)


@app.exception_handler(ImageNotFoundException)
async def image_not_found_exception_handler(request: Request, exc: ImageNotFoundException):
    return create_error_response(404, str(exc))


@app.exception_handler(InvalidImageFormatException)
async def invalid_image_format_exception_handler(request: Request, exc: InvalidImageFormatException):
    return create_error_response(400, str(exc))


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return create_error_response(422, str(exc))


@app.exception_handler(ImageUploadException)
async def image_upload_exception_handler(request: Request, exc: ImageUploadException):
    return create_error_response(500, str(exc))


@app.exception_handler(ImageDeletionException)
async def image_deletion_exception_handler(request: Request, exc: ImageDeletionException):
    return create_error_response(500, str(exc))


@app.exception_handler(StorageServiceException)
async def storage_service_exception_handler(request: Request, exc: StorageServiceException):
    return create_error_response(500, str(exc))


@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    return create_error_response(500, str(exc))