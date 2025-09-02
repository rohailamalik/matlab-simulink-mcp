import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from platformdirs import user_log_path

import matlab_simulink_mcp


def create_log_file(file: str) -> Path:
    """Resolve the path for the log file. Falls back to user log dir on permission errors."""
    
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent / "logs"
    else:
        base = Path(matlab_simulink_mcp.__file__).resolve().parents[2] / "logs"

    try:
        base.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        base = user_log_path("matlab_simulink_mcp")
        base.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Error creating log file directory: {e}")

    return base / file


def setup_logger(name: str = "matlab_simulink_mcp") -> logging.Logger:
    """Sets up a rotating file + stderr logger. """
    
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    log_path = create_log_file("matlab_simulink_mcp.log")

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(message)s %(filename)s:%(lineno)d",
        datefmt="[%m/%d/%y %H:%M:%S]",
    )

    fh = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.ERROR)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


logger = setup_logger()
