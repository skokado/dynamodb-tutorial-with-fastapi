from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, ClassVar

from app.clients import DynamoDBClient

from ._constants import DynamoDBTableName

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


@dataclass
class Session:
    table_name: ClassVar[str] = DynamoDBTableName.sessions

    client: DynamoDBClient = field(default_factory=DynamoDBClient)
    table: Table = field(init=False)

    def __post_init__(self) -> None:
        self.table = self.client.get_table(DynamoDBTableName.sessions)

    def create_session(
        self, user_id: str, session_id: str, ttl_seconds: int = 60 * 60
    ) -> str:
        now = datetime.now(timezone.utc)
        ttl = int(now.timestamp()) + ttl_seconds

        self.table.put_item(
            Item={
                "session_id": session_id,
                "user_id": user_id,
                "created_at": int(now.timestamp()),
                "ttl": ttl,
                "last_activity": int(now.timestamp()),
            }
        )
        return session_id

    def get_session(self, session_id: str) -> dict | None:
        response = self.table.get_item(Key={"session_id": session_id})
        return response.get("Item")

    def update_activity(self, session_id: str) -> None:
        self.table.update_item(
            Key={"session_id": session_id},
            UpdateExpression="SET last_activity = :now",
            ExpressionAttributeValues={
                ":now": int(datetime.now(timezone.utc).timestamp())
            },
        )
