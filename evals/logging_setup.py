import json
import logging
from pathlib import Path
from typing import TextIO

from rich.logging import RichHandler


class JsonlFileHandler(logging.Handler):
    def __init__(self, path: Path) -> None:
        super().__init__()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._stream: TextIO = path.open("a", encoding="utf-8")

    def emit(self, record: logging.LogRecord) -> None:
        try:
            payload = {
                "ts": record.created,
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            if record.exc_info:
                payload["exc"] = self.format(record)
            self._stream.write(json.dumps(payload) + "\n")
            self._stream.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        try:
            self._stream.close()
        finally:
            super().close()


def configure(level: str = "INFO", jsonl_sink: Path | None = None) -> None:
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    root.setLevel(level.upper())
    root.addHandler(RichHandler(rich_tracebacks=True, show_time=True, show_path=False))
    if jsonl_sink is not None:
        root.addHandler(JsonlFileHandler(jsonl_sink))
