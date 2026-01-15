from typing import ClassVar


class DynamoDBTableName:
    activities: ClassVar[str] = "UserActivities"
    comments: ClassVar[str] = "PostComments"
    likes: ClassVar[str] = "PostLikes"
    sessions: ClassVar[str] = "UserSessions"
