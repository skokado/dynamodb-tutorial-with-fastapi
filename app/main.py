from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI(title="DynamoDB Tutorial with FastAPI")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)


@app.get("/")
async def hello():
    return {"msg": "it works."}
