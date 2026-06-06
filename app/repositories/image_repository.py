from app.core.exception import DatabaseException
from app.core.logging import logger
from app.dbs.ddb import get_image_table
from boto3.dynamodb.conditions import Attr


class ImageRepository:

    @staticmethod
    def create_image(metadata: dict):
        logger.info("repository.create_image.start", extra={"image_id": metadata.get("image_id"), "user_id": metadata.get("user_id")})
        try:
            image_table = get_image_table()
            image_table.put_item(Item=metadata)
            logger.info("repository.create_image.success", extra={"image_id": metadata.get("image_id")})
        except Exception as exc:
            logger.exception("repository.create_image.failure", extra={"image_id": metadata.get("image_id"), "error": str(exc)})
            raise DatabaseException("Unable to save image metadata.") from exc

    @staticmethod
    def update_image(image_id: str, updates: dict):
        logger.info("repository.update_image.start", extra={"image_id": image_id, "updates": updates})
        try:
            image_table = get_image_table()
            update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in updates.keys())
            expression_attribute_names = {f"#{k}": k for k in updates.keys()}
            expression_attribute_values = {f":{k}": v for k, v in updates.items()}
            image_table.update_item(
                Key={"image_id": image_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
            )
            logger.info("repository.update_image.success", extra={"image_id": image_id})
        except Exception as exc:
            logger.exception("repository.update_image.failure", extra={"image_id": image_id, "error": str(exc)})
            raise DatabaseException("Unable to update image metadata.") from exc

    @staticmethod
    def get_image(image_id: str):
        logger.info("repository.get_image.start", extra={"image_id": image_id})
        try:
            image_table = get_image_table()
            response = image_table.get_item(
                Key={"image_id": image_id}
            )
            item = response.get("Item")
            logger.info("repository.get_image.success", extra={"image_id": image_id, "found": bool(item)})
            return item
        except Exception as exc:
            logger.exception("repository.get_image.failure", extra={"image_id": image_id, "error": str(exc)})
            raise DatabaseException("Unable to retrieve image metadata.") from exc

    @staticmethod
    def delete_image(image_id: str):
        logger.info("repository.delete_image.start", extra={"image_id": image_id})
        try:
            image_table = get_image_table()
            image_table.delete_item(
                Key={"image_id": image_id}
            )
            logger.info("repository.delete_image.success", extra={"image_id": image_id})
        except Exception as exc:
            logger.exception("repository.delete_image.failure", extra={"image_id": image_id, "error": str(exc)})
            raise DatabaseException("Unable to delete image metadata.") from exc

    @staticmethod
    def list_images(filters: dict):
        """List images using server-side filtering where possible.

        - If no filters provided, performs a full scan.
        - If `user_id` and/or `tag` are provided, builds a FilterExpression
          using `Attr` so DynamoDB will filter results server-side.
        """
        logger.info("repository.list_images.start", extra={"filters": filters})
        try:
            image_table = get_image_table()

            filter_expression = None

            user_id = filters.get("user_id")
            tag = filters.get("tag")

            if user_id:
                filter_expression = Attr("user_id").eq(user_id)

            if tag:
                tag_expr = Attr("tags").contains(tag)
                filter_expression = tag_expr if filter_expression is None else filter_expression & tag_expr

            if filter_expression is not None:
                response = image_table.scan(FilterExpression=filter_expression)
            else:
                response = image_table.scan()

        except Exception as exc:
            logger.exception("repository.list_images.failure", extra={"filters": filters, "error": str(exc)})
            raise DatabaseException("Unable to list images.") from exc

        items = response.get("Items", [])
        logger.info("repository.list_images.success", extra={"filters": filters, "count": len(items)})

        return items

    # @staticmethod
    # def update_image(image_id: str, updates: dict):
    #     logger.info("repository.update_image.start", extra={"image_id": image_id, "updates": updates})
    #     try:
    #         image_table = get_image_table()
    #         update_expression = "SET " + ", ".join(f"{k}=:{k}" for k in updates.keys())
    #         expression_attribute_values = {f":{k}": v for k, v in updates.items()}

    #         image_table.update_item(
    #             Key={"image_id": image_id},
    #             UpdateExpression=update_expression,
    #             ExpressionAttributeValues=expression_attribute_values
    #         )
    #         logger.info("repository.update_image.success", extra={"image_id": image_id})
    #     except Exception as exc:
    #         logger.exception("repository.update_image.failure", extra={"image_id": image_id, "error": str(exc)})
    #         raise DatabaseException("Unable to update image metadata.") from exc