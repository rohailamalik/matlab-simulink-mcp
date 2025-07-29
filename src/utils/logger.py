import logging
import os
from logging.handlers import RotatingFileHandler
from utils.utils import get_path
from config.settings import settings  

def setup_logger(name: str = "app"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_path = get_path(settings.logs_path) 
    log_file = os.path.join(logs_path, f"{name}.log")

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    if settings.mode.lower() == "dev":
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_fmt = logging.Formatter("%(levelname)s | %(message)s")
        console_handler.setFormatter(console_fmt)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger("mcp")
