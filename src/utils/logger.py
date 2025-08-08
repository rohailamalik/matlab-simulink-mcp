import logging
from logging.handlers import RotatingFileHandler
from utils.utils import get_path
from config.settings import settings  

def setup_logger(name: str = "app"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    log = get_path(settings.logs_path) / "log"
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    fh = RotatingFileHandler(log, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(logging.ERROR)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    if settings.mode.lower() == "dev":
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    return logger


logger = setup_logger("MMCP")
