import os

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Sqlite db
    sqlite_db_path: str

    # AWS
    aws_region: str
    aws_endpoint_url: str


config = Config(
    sqlite_db_path="..",
    aws_region=os.getenv(
        "AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1")
    ),
    aws_endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
)
