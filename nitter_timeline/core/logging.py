import logging
import sys

FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

_def_handlers_configured = False

def configure_logging(level: int = logging.INFO) -> None:
    global _def_handlers_configured
    if _def_handlers_configured:
        return
    logging.basicConfig(stream=sys.stdout, level=level, format=FORMAT)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    _def_handlers_configured = True
