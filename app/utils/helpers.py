"""Helper functions for the image service."""
from datetime import datetime
import time
import logging
import inspect

class Helpers:

    def timer_method(self, func):
        """Decorator to measure execution time of a function."""

        if inspect.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()
                logging.info(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
                return result

            return async_wrapper

        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            logging.info(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
            return result

        return wrapper

    def timestamp_to_iso8601(self, timestamp: float) -> str:
        """Convert a timestamp to ISO 8601 format."""
        return datetime.fromtimestamp(timestamp).isoformat() + 'Z'