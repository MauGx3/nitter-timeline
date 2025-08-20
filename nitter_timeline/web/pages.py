"""Page (HTML) routes using server-side templates."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="nitter_timeline/web/templates")

page_router = APIRouter()

@page_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main HTML shell.

    The timeline content hydrates client-side via a subsequent call to
    ``/api/timeline`` triggered by the embedded script.

    Args:
        request: Incoming FastAPI request (required by template engine).

    Returns:
        fastapi.responses.HTMLResponse: Rendered page.
    """
    return templates.TemplateResponse("index.html", {"request": request})
