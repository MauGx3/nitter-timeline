"""Application entry point exposing the FastAPI instance."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from nitter_timeline.api.routes import api_router
from nitter_timeline.core.config import settings as _settings  # noqa: F401
from nitter_timeline.core.logging import configure_logging
from nitter_timeline.core.security import add_security_middleware
from nitter_timeline.web.pages import page_router

configure_logging()

app = FastAPI(title="Nitter Timeline", version="0.1.0")
add_security_middleware(app)

app.include_router(page_router)
app.include_router(api_router, prefix="/api")

app.mount(
    "/static",
    StaticFiles(directory="nitter_timeline/web/static"),
    name="static",
)
 

@app.get("/healthz", summary="Health probe")
async def health() -> dict:
    """Return a minimal liveness indicator.

    Returns:
        dict: ``{"status": "ok"}`` when application is responsive.
    """
    return {"status": "ok"}
