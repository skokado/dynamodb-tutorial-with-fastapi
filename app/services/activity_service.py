from dataclasses import dataclass, field
from uuid import uuid4

from app.models.nosql import Activity as ActivityModel
from app.models.nosql import Comment as CommentModel
from app.models.nosql import Like as LikeModel
from app.models.nosql import Session as SessionModel


@dataclass
class ActivityService:
    activity_model: ActivityModel = field(default_factory=ActivityModel)
    comment_model: CommentModel = field(default_factory=CommentModel)
    like_model: LikeModel = field(default_factory=LikeModel)
    session_model: SessionModel = field(default_factory=SessionModel)

    def get_or_create_user(self, session_id: str) -> str:
        if session_id and (session := self.session_model.get_session(session_id)):
            self.session_model.update_activity(session_id)
            return session["user_id"]

        # 新規ユーザー作成
        user_id = "user_" + uuid4().hex[:32]
        self.session_model.create_session(user_id, session_id)
        return user_id

    def record_view(self, user_id: str, post_id: str) -> None:
        self.activity_model.record(
            user_id,
            "view",
            post_id,
        )

    def toggle_like(self, post_id: str, user_id: str) -> tuple[bool, int]:
        liked, count = self.like_model.toggle_like(post_id, user_id)
        if liked:
            self.activity_model.record(
                user_id,
                "like",
                post_id,
            )

        return liked, count

    def get_like_count(self, post_id: str) -> int:
        return self.like_model.fetch_likes_count(post_id)

    def has_user_likeed(self, post_id: str, user_id: str) -> bool:
        return self.like_model.has_liked(post_id, user_id)

    def add_comment(self, post_id: str, user_id: str, content: str) -> dict:
        comment = self.comment_model.add_comment(post_id, user_id, content)
        self.activity_model.record(
            user_id,
            "comment",
            post_id,
            metadata={
                "comment_id": comment["comment_id"],
            },
        )
        return comment

    def get_comments(self, post_id: str) -> list[dict]:
        return self.comment_model.fetch_comments(post_id)

    def get_recent_activities(
        self,
        activity_type: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        return self.activity_model.fetch_recent_activities(activity_type, limit)

    def get_post_activities(self, post_id: str) -> list[dict]:
        return self.activity_model.list_post_activities(post_id)
