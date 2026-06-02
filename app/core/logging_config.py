import logging
import sys
from pathlib import Path
from app.core.config import settings

Path("logs").mkdir(exist_ok=True)


class Utf8StreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream or sys.stdout)

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            stream.flush()
        except Exception:
            self.handleError(record)


def setup_logging():
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    formatter = logging.Formatter(log_format)

    console_handler = Utf8StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        handlers=[console_handler, file_handler],
    )

    return logging.getLogger("nlp_sql")


logger = setup_logging()
