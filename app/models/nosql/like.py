from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from app.clients import DynamoDBClient

from ._constants import DynamoDBTableName

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


@dataclass
class Like:
    """いいねカウンターテーブル（アトミックカウンター）"""

    table_name: ClassVar[str] = DynamoDBTableName.likes

    client: DynamoDBClient = field(default_factory=DynamoDBClient)
    table: Table = field(init=False)

    def __post_init__(self) -> None:
        self.table = self.client.get_table(DynamoDBTableName.likes)

    def toggle_like(self, post_id: str, user_id: str) -> tuple[bool, int]:
        response = self.table.get_item(Key={"post_id": post_id})
        item = response.get("Item", {"post_id": post_id, "count": 0, "users": []})
        users = item.get("users", [])
        if user_id in users:
            # いいね解除
            users.remove(user_id)
            response = self.table.update_item(
                Key={"post_id": post_id},
                UpdateExpression="ADD #count :dec SET users = :users",
                ExpressionAttributeNames={"#count": "count"},
                ExpressionAttributeValues={":dec": -1, ":users": users},
                ReturnValues="ALL_NEW",
            )
            return False, response["Attributes"]["count"]

        # いいね追加
        users.append(user_id)
        response = self.table.update_item(
            Key={"post_id": post_id},
            UpdateExpression="ADD #count :inc SET users = :users",
            ExpressionAttributeNames={"#count": "count"},
            ExpressionAttributeValues={":inc": 1, ":users": users},
            ReturnValues="ALL_NEW",
        )
        return True, response["Attributes"]["count"]

    def fetch_likes_count(self, post_id: str) -> int:
        response = self.table.get_item(Key={"post_id": post_id})
        return response.get("Item", {}).get("count", 0)

    def has_liked(self, post_id: str, user_id: str) -> bool:
        response = self.table.get_item(Key={"post_id": post_id})
        users = response.get("Item", {}).get("users", [])
        return user_id in users
