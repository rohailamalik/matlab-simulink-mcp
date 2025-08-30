import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from platformdirs import user_log_path


def setup_logger(name: str = "matlab_simulink_mcp") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s %(filename)s:%(lineno)d")
    datefmt="[%m/%d/%y %H:%M:%S]"
    
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt)

    logger.addHandler(ch)
    return logger

logger = setup_logger()