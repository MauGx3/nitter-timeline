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
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "ul",
]
ALLOWED_ATTRIBUTES: dict[str, list[str]] = {
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title", "loading", "decoding", "referrerpolicy"],
}
ALLOWED_PROTOCOLS = ["http", "https"]


def _post_process_images(html: str) -> str:
    """Inject safe default attributes for ``<img>`` tags.

    Adds lazy loading & async decoding if not present and a referrer policy.
    Avoids heavy HTML parsers by using a small regex on sanitized HTML.
    """
    import re  # local import to avoid cost if unused

    def repl(match: re.Match) -> str:  # type: ignore[name-defined]
        tag = match.group(0)
        # Ensure loading attribute
        if "loading=" not in tag:
            tag = tag[:-1] + ' loading="lazy">'
        if "decoding=" not in tag:
            tag = tag[:-1] + ' decoding="async">'
        if "referrerpolicy=" not in tag:
            tag = tag[:-1] + ' referrerpolicy="no-referrer">'
        if "class=" not in tag:
            tag = tag[:-1] + ' class="tl-img">'
        return tag

    return re.sub(r"<img\b[^>]*?>", repl, html, flags=re.IGNORECASE)


def sanitize_html(raw: str) -> str:
    """Return sanitized HTML (with limited tags) and enhanced images."""
    cleaned = bleach.clean(
        raw,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return _post_process_images(cleaned)
