import logging
import os
import sys
from contextvars import ContextVar
from typing import Optional
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
from fastapi import Request

REQUEST_ID_CTX: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
SERVICE_NAME = os.getenv("SERVICE_NAME", "image-service")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def get_request_id() -> str:
    return REQUEST_ID_CTX.get() or "-"


def set_request_id(request_id: str) -> None:
    REQUEST_ID_CTX.set(request_id)


def clear_request_id() -> None:
    REQUEST_ID_CTX.set(None)


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        record.service = SERVICE_NAME
        return True


def setup_logger() -> logging.Logger:
    logger = logging.getLogger(SERVICE_NAME)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(service)s %(request_id)s %(message)s'
        )
        handler.setFormatter(formatter)
        handler.addFilter(RequestContextFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or SERVICE_NAME)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        set_request_id(request_id)
        logger.info(
            "request_received",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "query": str(request.url.query),
                "request_id": request_id,
            },
        )

        try:
            response = await call_next(request)
            logger.info(
                "request_completed",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "request_id": request_id,
                },
            )
            return response
        except Exception:
            logger.exception(
                "request_error",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "request_id": request_id,
                },
            )
            raise
        finally:
            clear_request_id()