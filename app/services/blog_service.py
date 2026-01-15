from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rdb import BlogPost


@dataclass
class BlogService:
    def list_posts(self, db: Session) -> Sequence[BlogPost]:
        stmt = select(BlogPost).order_by(BlogPost.created_at.desc())
        posts = db.scalars(stmt).all()
        return posts

    def get_post(self, db: Session, post_id: int) -> BlogPost | None:
        stmt = select(BlogPost).where(BlogPost.id == post_id)
        return db.scalar(stmt)

    def create_post(
        self, db: Session, title: str, content: str, author: str
    ) -> BlogPost:
        new_post = BlogPost(
            title=title,
            content=content,
            author=author,
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post

    def update_post(
        self,
        db: Session,
        post_id: int,
        title: str | None = None,
        content: str | None = None,
    ) -> BlogPost | None:
        post = self.get_post(db, post_id)
        if post is None:
            return None

        if title is not None:
            post.title = title
        if content is not None:
            post.content = content

        db.commit()
        db.refresh(post)
        return post

    def delete_post(self, db: Session, post_id: int) -> bool:
        post = self.get_post(db, post_id)
        if post is None:
            return False

        db.delete(post)
        db.commit()
        return True

    def search_posts(self, db: Session, keyword: str) -> Sequence[BlogPost]:
        """キーワードでブログ記事を検索する"""
        stmt = select(BlogPost).where(
            BlogPost.title.contains(keyword) | BlogPost.content.contains(keyword)
        )
        posts = db.scalars(stmt).all()
        return posts
