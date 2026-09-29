from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db
from .routes import router


BASE_DIR = Path(
    __file__
).resolve().parent.parent


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered personalized "
        "fitness and wellness plan generator."
    ),
    version="1.0.0",
)


# Static files
app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static",
)


# Routes
app.include_router(router)


@app.on_event("startup")
def startup():

    init_db()