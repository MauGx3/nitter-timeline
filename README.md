# Nitter Timeline

Aggregate multiple Nitter RSS feeds (users, lists, searches) and present them in a unified, scrolling, near real‑time Twitter‑like timeline.

## Goals

- Input: list of Nitter RSS feed URLs (user timelines, list feeds, search queries via Nitter)
- Fetch & parse on schedule with caching + ETag / Last-Modified support when possible
- Merge + sort posts by published date
- De-duplicate by (link, guid)
- Provide lightweight web UI (FastAPI + HTMX or small JS) with infinite scroll & basic theming
- Allow simple rules (filter by keyword, author, reply/retweet type)

## Stack

- Python 3.11+
- FastAPI (API + server side rendered templates)
- Jinja2 templates + Tailwind (optional later) / minimal CSS first
- httpx + feedparser for fetching/parsing
- cachetools for in-memory caching (later: redis optional)

## Quick start

### 1. Create & activate a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

### 2. Install in editable mode (provides console script)

```bash
pip install -e .
```

### 3. Run the app (choose one)

Console script (preferred):

```bash
nitter-timeline --reload
```

Module form:

```bash
python -m nitter_timeline --reload
```

Direct uvicorn (still works):

```bash
uvicorn nitter_timeline.main:app --reload
```

Visit: <http://127.0.0.1:8000>

Flags available for the console script / module:

- `--host` (default `127.0.0.1` or `NT_SERVER_HOST` env)
- `--port` (default `8000` or `NT_SERVER_PORT` env)
- `--reload` (development auto-reload)

Environment overrides use the `NT_` prefix (see `core/config.py`). Example:

```bash
export NT_SERVER_PORT=9000
nitter-timeline
```

## Structure

```text
nitter_timeline/
  main.py              # FastAPI app + startup wiring
  core/config.py       # Settings management (env based)
  core/logging.py      # Logging setup
  models/feed.py       # Pydantic models for feed items
  services/fetcher.py  # Async fetch + cache logic
  services/aggregator.py # Merge/sort/filter logic
  api/routes.py        # APIRouter definitions
  web/templates/       # Jinja templates
  web/static/          # CSS/JS assets
```

## Next steps

- Implement config + models
- Build fetcher with concurrency & caching
- Implement aggregator & basic HTML timeline
- Add incremental API for pagination
- Add tests for parsing & aggregation

## Tooling

### Ruff

Ruff is configured (see `[tool.ruff]` in `pyproject.toml`) to provide fast linting (pyflakes/pycodestyle), import sorting, pyupgrade suggestions, and several quality rule sets (bugbear, simplify, async, naming, comprehensions). Run it locally:

```bash
ruff check .
ruff check . --fix  # apply safe autofixes
```

You can also sort imports & format (if later enabled) with:

```bash
ruff check --select I . --fix
```

Pylint remains for deeper design checks; over time some overlap can be reduced.

---

MIT License
