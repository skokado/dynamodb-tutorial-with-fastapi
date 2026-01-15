from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.clients import DynamoDBClient
from ._constants import DynamoDBTableName

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


@dataclass
class Activity:
    client: DynamoDBClient = field(init=False)
    table: Table = field(init=False)

    def __post_init__(self) -> None:
        self.client = DynamoDBClient()
        self.table = self.client.get_table(DynamoDBTableName.activities)

    def record(
        self,
        user_id: str,
        activity_type: str,
        post_id: int,
        metadata: dict | None = None,
    ) -> None: ...

    def fetch_user_activities(self, user_id: str, limit: int = 20) -> list[dict]: ...

    def fetch_recent_activities(
        self, activity_type: str | None = None, limit: int = 50
    ) -> list[dict]: ...

    def list_post_activities(self, post_id: int) -> list[dict]: ...
