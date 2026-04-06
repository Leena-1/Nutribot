from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        for k, v in record.__dict__.items():
            if k.startswith("_"):
                continue
            if k in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            ):
                continue
            # Only include JSON-serializable extras
            try:
                json.dumps(v)
                payload[k] = v
            except TypeError:
                payload[k] = str(v)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(*, level: str = "INFO", json_logs: bool = True) -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level.upper())
    handler.setFormatter(JsonFormatter() if json_logs else logging.Formatter("%(levelname)s %(name)s: %(message)s"))

    # Replace existing handlers (avoid duplicate logs in reload)
    root.handlers = [handler]

    # Quieter noisy libs
    logging.getLogger("uvicorn").setLevel(level.upper())
    logging.getLogger("uvicorn.error").setLevel(level.upper())
    logging.getLogger("uvicorn.access").setLevel(level.upper())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

