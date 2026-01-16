import secrets
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

from fastapi import Cookie, Depends, FastAPI, Form, Request
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
    session_id: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
):
    if new_user := session_id is None:
        session_id = generate_session_id()

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
    if new_user:
        response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response


def generate_session_id() -> str:
    return "sess_" + secrets.token_hex(128)


@app.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(
    request: Request,
    post_id: int,
    session_id: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
):
    if new_user := session_id is None:
        session_id = generate_session_id()

    user_id = activity_service.get_or_create_user(session_id)
    activity_service.record_view(user_id, str(post_id))

    response = templates.TemplateResponse(
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
    if new_user:
        response.set_cookie(key="session_id", value=session_id, httponly=True)

    return response


@app.post("/post/{post_id}/like")
async def toggle_like(post_id: int, session_id: Annotated[str | None, Cookie()] = None):
    if not session_id:
        return

    user_id = activity_service.get_or_create_user(session_id)

    liked, count = activity_service.toggle_like(str(post_id), user_id)

    # htmx用の部分更新レスポンス
    return f"""
    <button hx-post="/post/{post_id}/like" 
            hx-target="this" 
            hx-swap="outerHTML"
            class="like-btn {"liked" if liked else ""}">
        {"❤️" if liked else "🤍"} {count}
    </button>
    """


@app.post("/post/{post_id}/comment")
async def add_comment(
    post_id: int,
    content: str = Form(...),
    session_id: Annotated[str | None, Cookie()] = None,
):
    if not session_id:
        return

    user_id = activity_service.get_or_create_user(session_id)

    comment = activity_service.add_comment(str(post_id), user_id, content)

    # htmx用の部分更新レスポンス
    return f"""
    <div class="comment">
        <div class="comment-header">{user_id[:8]}... - {datetime.fromtimestamp(comment["timestamp"]).strftime("%Y-%m-%d %H:%M")}</div>
        <div class="comment-content">{comment["content"]}</div>
    </div>
    """


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


@app.post("/post/create")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(...),
    db: Session = Depends(get_db),
):
    post = blog_service.create_post(db, title, content, author)
    return {"id": post.id, "message": "Post created successfully"}
