import logging
import sys
from pathlib import Path
from app.core.config import settings

Path("logs").mkdir(exist_ok=True)


def setup_logging():
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log"),
        ],
    )
    return logging.getLogger("nlp_sql")


logger = setup_logging()
