from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.clients import DynamoDBClient
from ._constants import DynamoDBTableName

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


@dataclass
class Session:
    client: DynamoDBClient = field(init=False)
    table: Table = field(init=False)

    def __post_init__(self) -> None:
        self.client = DynamoDBClient()
        self.table = self.client.get_table(DynamoDBTableName.sessions)

    def create_session(self, user_id: str) -> str: ...

    def get_session(self, session_id: str) -> dict | None: ...

    def update_activity(self, session_id: str) -> None: ...
