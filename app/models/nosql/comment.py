from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, ClassVar
from uuid import uuid4

from app.clients import DynamoDBClient

from ._constants import DynamoDBTableName

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


@dataclass
class Comment:
    """コメントテーブル（階層データ）"""

    table_name: ClassVar[str] = DynamoDBTableName.comments

    client: DynamoDBClient = field(default_factory=DynamoDBClient)
    table: Table = field(init=False)

    def __post_init__(self) -> None:
        self.table = self.client.get_table(DynamoDBTableName.comments)

    def add_comment(
        self,
        post_id: str,
        user_id: str,
        content: str,
        parent_comment_id: int | None = None,
    ) -> dict:
        comment_id = f"{int(datetime.now(timezone.utc).timestamp())}_{uuid4().hex[:8]}"

        item: dict[str, Any] = {
            "post_id": post_id,
            "comment_id": comment_id,
            "user_id": user_id,
            "content": content,
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "parent_id": parent_comment_id,
            "replies": [],
        }

        self.table.put_item(Item=item)

        # 親コメントがある場合 replies を更新
        if parent_comment_id is not None:
            self.table.update_item(
                Key={"post_id": post_id, "comment_id": parent_comment_id},
                UpdateExpression="SET replies = list_append(if_not_exists(replies, :empty), :new_reply)",
                ExpressionAttributeValues={":empty": [], ":new_reply": [comment_id]},
            )

        return item

    def fetch_comments(self, post_id: str) -> list[dict]:
        response = self.table.query(
            KeyConditionExpression="post_id = :pid",
            ExpressionAttributeValues={":pid": post_id},
        )
        return response["Items"]
