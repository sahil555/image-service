from app.core.exception import DatabaseException
from app.dbs.ddb import get_image_table
from boto3.dynamodb.conditions import Attr


class ImageRepository:

    @staticmethod
    def create_image(metadata: dict):
        try:
            image_table = get_image_table()
            image_table.put_item(Item=metadata)
        except Exception as exc:
            raise DatabaseException("Unable to save image metadata.") from exc

    @staticmethod
    def get_image(image_id: str):
        try:
            image_table = get_image_table()
            response = image_table.get_item(
                Key={"image_id": image_id}
            )
            return response.get("Item")
        except Exception as exc:
            raise DatabaseException("Unable to retrieve image metadata.") from exc

    @staticmethod
    def delete_image(image_id: str):
        try:
            image_table = get_image_table()
            image_table.delete_item(
                Key={"image_id": image_id}
            )
        except Exception as exc:
            raise DatabaseException("Unable to delete image metadata.") from exc

    @staticmethod
    def list_images(filters: dict):
        """List images using server-side filtering where possible.

        - If no filters provided, performs a full scan.
        - If `user_id` and/or `tag` are provided, builds a FilterExpression
          using `Attr` so DynamoDB will filter results server-side.
        """
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
            raise DatabaseException("Unable to list images.") from exc

        items = response.get("Items", [])

        return items
