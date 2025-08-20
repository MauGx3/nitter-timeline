"""HTML sanitization helpers."""
from __future__ import annotations

import bleach

ALLOWED_TAGS: list[str] = [
    "a",
    "abbr",
    "b",
    "blockquote",
    "br",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "ul",
]
ALLOWED_ATTRIBUTES: dict[str, list[str]] = {"a": ["href", "title", "rel"]}
ALLOWED_PROTOCOLS = ["http", "https"]


def sanitize_html(raw: str) -> str:
    """Return sanitized HTML limited to a safe subset.

    Args:
        raw: Untrusted HTML snippet.

    Returns:
        str: Cleaned HTML.
    """
    return bleach.clean(
        raw,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
