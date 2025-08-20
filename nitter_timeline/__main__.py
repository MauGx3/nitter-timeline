"""CLI entrypoint to run the ASGI app with uvicorn.

Allows launching via the console script ``nitter-timeline`` or
``python -m nitter_timeline``.
"""
from __future__ import annotations

import argparse
import importlib
import sys

import uvicorn

from .core.config import settings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Nitter Timeline server")
    parser.add_argument(
        "--host",
        default=settings.server_host,
        help="Bind host (default from settings)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.server_port,
        help="Bind port (default from settings)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (dev only)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - trivial
    args = parse_args(argv)
    # Lazy import to ensure side effects (logging) happen correctly
    module = importlib.import_module("nitter_timeline.main")
    app = module.app  # type: ignore[attr-defined]
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
