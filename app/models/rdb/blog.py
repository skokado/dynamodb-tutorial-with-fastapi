from datetime import datetime, timezone

import sqlalchemy as sa

from app.database import Base, engine


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(255), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    author = sa.Column(sa.String(100), nullable=False)
    created_at = sa.Column(
        sa.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


Base.metadata.create_all(engine)
