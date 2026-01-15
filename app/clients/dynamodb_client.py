from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import boto3

from app.config import config


if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table


@dataclass(frozen=True)
class DynamoDBClient:
    resource: DynamoDBServiceResource = field(init=False)

    def __post_init__(self) -> None:
        dynamodb: DynamoDBServiceResource = boto3.resource(
            "dynamodb",
            endpoint_url=config.aws_endpoint_url,
            region_name=config.aws_region,
        )
        # https://stackoverflow.com/a/54119384
        object.__setattr__(
            self,
            "resource",
            dynamodb,
        )

    def get_table(self, table_name: str) -> Table:
        return self.resource.Table(table_name)
