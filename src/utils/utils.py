from pathlib import Path
from project_root import root_path
from typing import Any
from utils.logger import logger


def get_path(relative_path: str) -> Path:
    return root_path / relative_path


def get_cwd(eng) -> Path:
    """Safely extracts current MATLAB working directory."""
    try:
        return Path(str(eng.pwd(nargout=1)))
    except Exception as e:
        raise RuntimeError(f"Unexpected error while getting current working directory: {e}")


def res(content: Any) -> dict:
    """Returns a dictionary for tool returns in case of successful execution."""
    return {"status": "Success", "Content": content}


def err(content: Any, log: bool = True, security = False) -> dict:
    """
    Returns a dictionary for tool returns in case of an error.
    Also logs the error to console and file (unless specified).
    Logs a critical error in case of security related cases (e.g. a forbidden command used etc).
    """
    if log:
        if security:
            logger.critical(content)
        else:
            logger.exception(content)

    return {"status": "Error", "Content": content}

