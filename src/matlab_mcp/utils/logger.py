import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from platformdirs import user_log_path

import matlab_mcp


def create_log_file(file: str) -> Path:
    if getattr(sys, "frozen", False): 
        dir = Path(sys.executable).parent / "logs" / file
    else:
        dir = Path(matlab_mcp.__file__).resolve().parent / "logs" / file

    try: 
        dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        dir = user_log_path("matlab_mcp") / file
        dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Error creating log file: {e}")                 


def setup_logger(name: str = "MATLAB_MCP") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    log_path = create_log_file("matlab_mcp.log")
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    fh = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.ERROR)
    fh.setFormatter(fmt)

    if not getattr(sys, "frozen", False):
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = setup_logger()