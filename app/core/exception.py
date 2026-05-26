"""
Custom exceptions for the image service.
"""
# defining custom exceptions allows us to provide more specific error messages and handle different error scenarios gracefully in our application.
from email.mime import message
import logging

logging.basicConfig(level=logging.ERROR)

class ImageNotFoundException(Exception):
    """Raised when an image is not found in the database."""

    def __init__(self, image_id: str):
        logging.error("Image not found in the database.")
        self.image_id = image_id
        super().__init__(f"Image with ID {image_id} not found.")
    

class ImageUploadException(Exception):
    """Raised when there is an error during image upload."""

    def __init__(self, message: str):
        logging.error("Error occurred while uploading image.")
        super().__init__(message)

    
    

class ImageDeletionException(Exception):
    """Raised when there is an error during image deletion."""
    def __init__(self, message: str):
        logging.error("Error occurred while deleting image.")
        super().__init__(message)

class InvalidImageFormatException(Exception):
    """Raised when the uploaded file is not a valid image format."""
    def __init__(self, message: str):
        logging.error("Invalid image format.")
        super().__init__(message)

class StorageServiceException(Exception):
    """Raised when there is an error with the storage service."""
    def __init__(self, message: str):
        logging.error("Error occurred with the storage service.")
        super().__init__(message)

class DatabaseException(Exception):
    """Raised when there is an error with the database operations."""
    def __init__(self, message: str):
        logging.error("Error occurred with the database.")
        super().__init__(message)

class ValidationException(Exception):
    """Raised when there is a validation error with the input data."""
    def __init__(self, message: str):
        logging.error("Validation error with the input data.")
        super().__init__(message)