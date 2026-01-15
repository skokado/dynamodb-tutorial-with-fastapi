from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, ClassVar

from app.clients import DynamoDBClient

from ._constants import DynamoDBTableName

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


@dataclass
class Activity:
    """ユーザーアクティビティテーブル（時系列データ）"""

    table_name: ClassVar[str] = DynamoDBTableName.activities

    client: DynamoDBClient = field(default_factory=DynamoDBClient)
    table: Table = field(init=False)

    def __post_init__(self) -> None:
        self.table = self.client.get_table(DynamoDBTableName.activities)

    def record(
        self,
        user_id: str,
        activity_type: str,
        post_id: str,
        metadata: dict | None = None,
    ) -> dict:
        item: dict[str, Any] = {
            "user_id": user_id,
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "activity_type": activity_type,  # 'view', 'like', 'comment', 'share'
            "post_id": post_id or "none",
            "metadata": metadata or {},
        }

        self.table.put_item(Item=item)
        return item

    def fetch_user_activities(self, user_id: str, limit: int = 20) -> list[dict]:
        response = self.table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id},
            ScanIndexForward=False,
            Limit=limit,
        )
        return response["Items"]

    def fetch_recent_activities(
        self, activity_type: str | None = None, limit: int = 50
    ) -> list[dict]:
        if activity_type is None:
            response = self.table.scan(Limit=limit)
        else:
            response = self.table.query(
                IndexName="ActivityTypeIndex",
                KeyConditionExpression="activity_type = :type",
                ExpressionAttributeValues={":type": activity_type},
                ScanIndexForward=False,
                Limit=limit,
            )

        return response["Items"]

    def list_post_activities(self, post_id: str) -> list[dict]:
        response = self.table.query(
            IndexName="PostIdIndex",
            KeyConditionExpression="post_id = :pid",
            ExpressionAttributeValues={":pid": post_id},
            ScanIndexForward=False,
        )
        return response["Items"]
