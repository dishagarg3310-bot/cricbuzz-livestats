import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    """Log to the console, and to logs/app.log when the folder is writable."""
    root = logging.getLogger()
    if getattr(root, "_livestats_ready", False):
        return

    formatter = logging.Formatter(LOG_FORMAT)
    root.setLevel(level)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    try:
        LOG_DIR.mkdir(exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_DIR / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    except OSError:
        root.warning("Could not write logs/app.log, logging to the console only.")

    root._livestats_ready = True