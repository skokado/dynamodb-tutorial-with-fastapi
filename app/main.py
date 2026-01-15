from pathlib import Path
from typing import Optional

from fastapi import Cookie, FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import ActivityService, BlogService

app = FastAPI(title="DynamoDB Tutorial with FastAPI")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)

activity_service = ActivityService()
blog_service = BlogService()


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    session_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    user_id = activity_service.get_or_create_user(session_id)
    posts = blog_service.list_posts(db)

    recent_activities = activity_service.get_recent_activities(limit=10)

    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": posts,
            "recent_activities": recent_activities,
            "user_id": user_id,
        },
    )
    return response


@app.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(
    request: Request,
    post_id: int,
    session_id: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    user_id = activity_service.get_or_create_user(session_id)
    activity_service.record_view(user_id, str(post_id))

    return templates.TemplateResponse(
        "post_detail.html",
        {
            "request": request,
            "post": blog_service.get_post(db, post_id),
            "like_count": activity_service.get_like_count(str(post_id)),
            "has_liked": activity_service.has_user_likeed(str(post_id), user_id),
            "comments": activity_service.get_comments(str(post_id)),
            "activities": activity_service.get_post_activities(str(post_id)),
            "user_id": user_id,
        },
    )


@app.get("/activities/feed")
async def activity_feed(activity_type: str | None = None):
    activities = activity_service.get_recent_activities(activity_type)
    return templates.TemplateResponse(
        "components/activity_feed.html",
        {
            "request": {},
            "activities": activities,
        },
    )
