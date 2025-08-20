from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api.routes import api_router
from .core.config import settings
from .core.logging import configure_logging
from .web.pages import page_router

configure_logging()

app = FastAPI(title="Nitter Timeline", version="0.1.0")

app.include_router(page_router)
app.include_router(api_router, prefix="/api")

app.mount("/static", StaticFiles(directory="nitter_timeline/web/static"), name="static")

@app.get("/healthz")
async def health() -> dict:
    return {"status": "ok"}
