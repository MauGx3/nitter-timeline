"""Logging configuration utilities."""
# pylint: disable=no-member
import logging
import sys

FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

_def_handlers_configured = False

 
def configure_logging(level: int = logging.INFO) -> None:
    """Configure application logging.

    Idempotent: subsequent invocations are ignored to avoid duplicate
    handlers. Adjusts noisy third-party library loggers (e.g. ``httpx``).

    Args:
        level: Root logger level (defaults to ``logging.INFO``).
    """
    global _def_handlers_configured  # pylint: disable=global-statement
    if _def_handlers_configured:
        return
    logging.basicConfig(stream=sys.stdout, level=level, format=FORMAT)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    _def_handlers_configured = True
