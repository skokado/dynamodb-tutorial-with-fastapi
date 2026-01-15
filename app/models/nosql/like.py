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

    client: DynamoDBClient = field(init=False)
    table: Table = field(init=False)

    def __post_init__(self) -> None:
        self.client = DynamoDBClient()
        self.table = self.client.get_table(DynamoDBTableName.likes)

    def toggle_like(self, post_id: int, user_id: str) -> tuple[bool, int]: ...

    def fetch_likes_count(self, post_id: int) -> int: ...

    def has_liked(self, post_id: int, user_id: str) -> bool: ...
