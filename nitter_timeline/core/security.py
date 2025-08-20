"""Security related middleware and helpers."""
from __future__ import annotations

from collections.abc import Callable

from starlette.types import ASGIApp, Receive, Scope, Send

from nitter_timeline.core.config import settings


class SecurityHeadersMiddleware:
    """Inject common security headers.

    Controlled via settings; designed to be inexpensive.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:  # type: ignore[override]
        if (
            scope.get("type") != "http"
            or not settings.security_headers_enabled
        ):
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):  # type: ignore[no-untyped-def]
            if message.get("type") == "http.response.start":
                headers = message.setdefault("headers", [])
                csp_parts = [
                    "default-src 'self'",
                    "img-src 'self' data: https:",
                    "style-src 'self'",
                    "object-src 'none'",
                    "frame-ancestors 'none'",
                    "base-uri 'none'",
                    "form-action 'self'",
                ]
                if settings.csp_allow_inline_scripts:
                    csp_parts.append("script-src 'self' 'unsafe-inline'")
                else:
                    csp_parts.append("script-src 'self'")
                csp_value = "; ".join(csp_parts)

                def _add(k: str, v: str) -> None:
                    headers.append((k.lower().encode(), v.encode()))

                _add("content-security-policy", csp_value)
                _add("x-content-type-options", "nosniff")
                _add("x-frame-options", "DENY")
                _add("referrer-policy", "no-referrer")
                _add(
                    "permissions-policy",
                    "geolocation=(), microphone=(), camera=()",
                )
                _add(
                    "strict-transport-security",
                    "max-age=63072000; includeSubDomains; preload",
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)


def add_security_middleware(app: Callable) -> None:
    """Helper to attach middleware if enabled."""
    if settings.security_headers_enabled:
        app.add_middleware(  # type: ignore[attr-defined]
            SecurityHeadersMiddleware
        )
