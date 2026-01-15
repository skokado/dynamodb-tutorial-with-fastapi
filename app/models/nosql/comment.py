from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

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
    ) -> dict: ...

    def fetch_comments(self, post_id: str) -> list[dict]: ...
