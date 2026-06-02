"""
Custom exceptions for the image service.
"""
# defining custom exceptions allows us to provide more specific error messages and handle different error scenarios gracefully in our application.

from app.core.logging import logger

class ImageNotFoundException(Exception):
    """Raised when an image is not found in the database."""

    def __init__(self, image_id: str):
        logger.error("Image not found in the database.", extra={"image_id": image_id})
        self.image_id = image_id
        super().__init__(f"Image with ID {image_id} not found.")


class ImageUploadException(Exception):
    """Raised when there is an error during image upload."""

    def __init__(self, message: str):
        logger.error("Error occurred while uploading image.", extra={"error": message})
        super().__init__(message)


class ImageDeletionException(Exception):
    """Raised when there is an error during image deletion."""

    def __init__(self, message: str):
        logger.error("Error occurred while deleting image.", extra={"message": message})
        super().__init__(message)


class InvalidImageFormatException(Exception):
    """Raised when the uploaded file is not a valid image format."""

    def __init__(self, message: str):
        logger.error("Invalid image format.", extra={"message": message})
        super().__init__(message)


class StorageServiceException(Exception):
    """Raised when there is an error with the storage service."""

    def __init__(self, message: str):
        logger.error("Error occurred with the storage service.", extra={"message": message})
        super().__init__(message)


class DatabaseException(Exception):
    """Raised when there is an error with the database operations."""
    def __init__(self, message: str):
        logger.error("Error occurred with the database.", extra={"message": message})
        super().__init__(message)

class ValidationException(Exception):
    """Raised when there is a validation error with the input data."""

    def __init__(self, message: str):
        logger.error("Validation error with the input data.", extra={"message": message})
        super().__init__(message)