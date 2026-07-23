"""Structured JSON logging configuration.

Format: JSON lines, one log entry per line.
Fields: timestamp, level, logger, request_id, user_id, method, path, duration_ms, message.

No PII is ever logged. Roll numbers, device fingerprints, and tokens are excluded.
"""

import logging
import logging.config
import sys

from pythonjsonlogger.jsonlogger import JsonFormatter

from app.core.config import settings


LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(timestamp)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if settings.ENVIRONMENT != "development" else "verbose",
            "stream": sys.stdout,
        },
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["console"],
    },
}


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)  # type: ignore[attr-defined]


# Convenience logger for this app
logger = logging.getLogger("constellation")
