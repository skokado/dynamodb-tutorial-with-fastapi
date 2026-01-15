#!/usr/bin/env python3
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, Path(__file__).parent.parent.as_posix())

import click

from app.database import SessionLocal
from app.models.rdb import BlogPost


@click.command()
def cli():
    """初期データ作成"""

    with SessionLocal() as db:
        if db.query(BlogPost).first() is not None:
            click.echo("初期データは既に作成されています。")
            return

        sample_posts = [
            {
                "title": "DynamoDBの基礎",
                "content": "NoSQLデータベースの特徴について...",
                "author": "admin",
            },
            {
                "title": "パーティションキーの設計",
                "content": "効率的なキー設計の重要性...",
                "author": "admin",
            },
            {
                "title": "GSIの活用方法",
                "content": "グローバルセカンダリインデックスの使い方...",
                "author": "tech_writer",
            },
        ]

        for post_data in sample_posts:
            post = BlogPost(**post_data)
            db.add(post)

        db.commit()


if __name__ == "__main__":
    cli()
