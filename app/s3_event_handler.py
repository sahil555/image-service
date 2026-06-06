import time
from typing import Any

from app.repositories.image_repository import ImageRepository
from app.core.exception import DatabaseException
from app.core.logging import logger
from app.utils.helpers import Helpers


def handler(event: dict[str, Any], context: Any):
    logger.info("s3_event_handler.request", extra={"event_records": len(event.get("Records", []))})

    for record in event.get("Records", []):
        event_name = record.get("eventName", "")
        if not event_name.startswith("ObjectCreated"):
            logger.info("s3_event_handler.skipping_non_object_created", extra={"event_name": event_name})
            continue

        s3_record = record.get("s3", {})
        bucket = s3_record.get("bucket", {}).get("name")
        key = s3_record.get("object", {}).get("key")
        if not key or not key.startswith("images/"):
            logger.warning("s3_event_handler.invalid_key", extra={"bucket": bucket, "key": key})
            continue

        image_id = key.split("/", 1)[-1]
        uploaded_at = Helpers().timestamp_to_iso8601(time.time())
        update_payload = {
            "status": "UPLOADED",
            "uploaded_at": uploaded_at,
            "s3_key": key,
        }

        try:
            existing = ImageRepository.get_image(image_id)
            if existing:
                ImageRepository.update_image(image_id, update_payload)
                logger.info("s3_event_handler.metadata_updated", extra={"image_id": image_id})
            else:
                ImageRepository.create_image({"image_id": image_id, **update_payload})
                logger.info("s3_event_handler.metadata_created", extra={"image_id": image_id})
        except DatabaseException as exc:
            logger.error("s3_event_handler.database_failure", extra={"image_id": image_id, "error": str(exc)})
            raise

    return {"status": "processed", "records": len(event.get("Records", []))}
