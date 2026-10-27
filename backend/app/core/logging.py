import logging
import json
import traceback
from logging.config import dictConfig
from datetime import datetime, timezone


class ApplicationFormatter(logging.Formatter):
    """Keep ordinary logs readable and emit event records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        event = getattr(record, "event", None)
        if not event:
            return super().format(record)

        payload = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": event,
            "stage": getattr(record, "stage", None),
            "country_code": getattr(record, "country_code", None),
            "error_type": getattr(record, "error_type", None),
        }
        if record.exc_info:
            payload["traceback"] = "".join(traceback.format_exception(*record.exc_info))
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(debug: bool) -> None:
    level = "DEBUG" if debug else "INFO"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "app.core.logging.ApplicationFormatter",
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "access": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(client_addr)s - \"%(request_line)s\" %(status_code)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "access_console": {
                    "class": "logging.StreamHandler",
                    "formatter": "access",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": level,
                "handlers": ["console"],
            },
            "loggers": {
                "app": {
                    "level": level,
                    "propagate": True,
                },
                "uvicorn": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": level,
                    "handlers": ["access_console"],
                    "propagate": False,
                },
            },
        }
    )

    logging.getLogger(__name__).info("Application logging initialized")
    logging.getLogger(__name__).info("DEBUG mode: %s", debug)
