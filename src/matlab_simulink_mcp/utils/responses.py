from typing import Any
from matlab_simulink_mcp.utils.logger import logger


def answer(content: Any) -> dict:
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