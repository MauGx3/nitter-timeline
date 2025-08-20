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

(After dependencies installed)

```bash
uvicorn nitter_timeline.main:app --reload
```

Open <http://127.0.0.1:8000>

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
