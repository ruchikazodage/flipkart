import logging
from pathlib import Path
from datetime import datetime



ROOT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / f"test_{datetime.now().strftime('%Y-%m-%d')}.log"


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler = logging.FileHandler(
            LOG_FILE,
            mode="a",
            encoding="utf-8"
        )

        #file_handler.setFormatter(formatter)

        #logger.addHandler(file_handler)

    return logging.getLogger(name)
