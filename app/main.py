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
from app.core.logging import logger, set_request_id, clear_request_id, LoggingMiddleware



def create_error_response(status_code: int, message: str):
    return JSONResponse(status_code=status_code, content={"detail": message})


app = FastAPI(
    title="Image Service API",
    version="1.0.0"
)

app.add_middleware(LoggingMiddleware)

app.include_router(image_router)


@app.exception_handler(ImageNotFoundException)
async def image_not_found_exception_handler(request: Request, exc: ImageNotFoundException):
    logger.error("image_not_found_exception", extra={"path": str(request.url.path), "error": str(exc)})
    return create_error_response(404, str(exc))


@app.exception_handler(InvalidImageFormatException)
async def invalid_image_format_exception_handler(request: Request, exc: InvalidImageFormatException):
    logger.error("invalid_image_format_exception", extra={"path": str(request.url.path), "error": str(exc)})
    return create_error_response(400, str(exc))


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    logger.error("validation_exception", extra={"path": str(request.url.path), "error": str(exc)})
    return create_error_response(422, str(exc))


@app.exception_handler(ImageUploadException)
async def image_upload_exception_handler(request: Request, exc: ImageUploadException):
    logger.error("image_upload_exception", extra={"path": str(request.url.path), "error": str(exc)})
    return create_error_response(500, str(exc))


@app.exception_handler(ImageDeletionException)
async def image_deletion_exception_handler(request: Request, exc: ImageDeletionException):
    logger.error("image_deletion_exception", extra={"path": str(request.url.path), "error": str(exc)})
    return create_error_response(500, str(exc))


@app.exception_handler(StorageServiceException)
async def storage_service_exception_handler(request: Request, exc: StorageServiceException):
    logger.error("storage_service_exception", extra={"path": str(request.url.path), "error": str(exc)})
    return create_error_response(500, str(exc))


@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    logger.error("database_exception", extra={"path": str(request.url.path), "message": str(exc)})
    return create_error_response(500, str(exc))