#!/usr/bin/env python3
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, Path(__file__).parent.parent.as_posix())

import click

from app.clients import DynamoDBClient
from app.models.nosql import Activity, Comment, Like, Session


def _create_activities_table(client: DynamoDBClient) -> None:
    table = client.resource.create_table(
        TableName=Activity.table_name,
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "N"},
            {"AttributeName": "activity_type", "AttributeType": "S"},
            {"AttributeName": "post_id", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "ActivityTypeIndex",
                "KeySchema": [
                    {"AttributeName": "activity_type", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "PostActivityIndex",
                "KeySchema": [
                    {"AttributeName": "post_id", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def _create_likes_table(client: DynamoDBClient) -> None:
    table = client.resource.create_table(
        TableName=Like.table_name,
        KeySchema=[
            {"AttributeName": "post_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[{"AttributeName": "post_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


def _create_comments_table(client: DynamoDBClient) -> None:
    table = client.resource.create_table(
        TableName=Comment.table_name,
        KeySchema=[
            {"AttributeName": "post_id", "KeyType": "HASH"},
            {"AttributeName": "comment_id", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "post_id", "AttributeType": "S"},
            {"AttributeName": "comment_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def _create_sessions_table(client: DynamoDBClient) -> None:
    table = client.resource.create_table(
        TableName=Session.table_name,
        KeySchema=[
            {"AttributeName": "session_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "session_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    # ttl設定
    client.resource.meta.client.update_time_to_live(
        TableName=Session.table_name,
        TimeToLiveSpecification={
            "Enabled": True,
            "AttributeName": "ttl",
        },
    )


@click.command()
def cli():
    client = DynamoDBClient()

    # Activity Table
    click.echo(f"Creating table: {Activity.table_name}")
    try:
        _create_activities_table(client)
    except Exception as e:
        click.echo(
            f"Table {Activity.table_name} already exists or error on creation: {e}",
            color=True,
        )
    else:
        click.echo(f"Table {Activity.table_name} created successfully.")

    # Like Table
    click.echo(f"Creating table: {Like.table_name}")
    try:
        _create_likes_table(client)
    except Exception as e:
        click.echo(
            f"Table {Like.table_name} already exists or error on creation: {e}",
            color=True,
        )
    else:
        click.echo(f"Table {Like.table_name} created successfully.")

    # Comment Table
    click.echo(f"Creating table: {Comment.table_name}")
    try:
        _create_comments_table(client)
    except Exception as e:
        click.echo(
            f"Table {Comment.table_name} already exists or error on creation: {e}",
            color=True,
        )
    else:
        click.echo(f"Table {Comment.table_name} created successfully.")

    # Session Table
    click.echo(f"Creating table: {Session.table_name}")
    try:
        _create_sessions_table(client)
    except Exception as e:
        click.echo(
            f"Table {Session.table_name} already exists or error on creation: {e}",
            color=True,
        )
    else:
        click.echo(f"Table {Session.table_name} created successfully.")


if __name__ == "__main__":
    cli()
