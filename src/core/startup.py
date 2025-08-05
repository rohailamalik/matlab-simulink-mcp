from config.settings import settings
from utils.logger import logger
from utils.utils import get_path
import pickle 
import json
from typing import Optional
from pathlib import Path


def load_server_data() -> Optional[dict]:
    if not settings.sl_lib_data_path:
        logger.error("Server data path not configured.")
        return None

    path = get_path(settings.sl_lib_data_path)  # ensures absolute Path
    ext = path.suffix.lower()

    try:
        if ext == ".json":
            with path.open("r", encoding="utf-8") as f:
                logger.info(f"Server data loaded from JSON: {path}")
                return json.load(f)

        elif ext in {".pkl", ".pickle"}:
            with path.open("rb") as f:
                logger.info(f"Server data loaded from Pickle: {path}")
                return pickle.load(f)

        logger.error(f"Unsupported server data file extension: {ext}")

    except FileNotFoundError:
        logger.error(f"Server data file not found: {path}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in: {path}")
    except pickle.UnpicklingError:
        logger.error(f"Invalid Pickle format in: {path}")
    except Exception:
        logger.error("Unexpected error while loading server data", exc_info=True)

    return None


def set_helpers(eng) -> str:
    if not settings.matlab_helpers_path:
        logger.warning("MATLAB helpers path not set.")
        return None

    path = get_path(settings.matlab_helpers_path)

    if not path.is_dir():
        logger.error(f"MATLAB helpers directory not found: {path}")

    files = [f for f in path.iterdir() if f.suffix == ".m"]

    if not files:
        logger.warning(f"No .m files found in helpers directory: {path}")

    try:
        eng.addpath(str(path), nargout=0)
        logger.info("MATLAB helper functions added to path successfully.")
        return str(path)

    except Exception:
        logger.error("Failed to add MATLAB helper path", exc_info=True)
        return None


def set_cwd(eng):
    """
    Returns path to the current working directory. 
    The LLM strictly cannot go outside this working directory and will only execute code through a temporary file in this directory.
    """
    try:
        logger.info("Getting current working directory")
        path = Path(str(eng.pwd))
        logger.info("Got current working directory")
        return path
    except Exception:
        logger.error("Unexpected error while getting current working directory", exc_info=True)
        return None
    
def set_security(eng):
    try: 
        path = settings.security_wrappers_path
        if settings.advanced_security:
            eng.addpath(str(path), '-begin', nargout=0)
        logger.info(f"Security level set to: {settings.advanced_security}")
        return path
    except Exception:
        logger.error("Unexpected error while getting setting up security mode", exc_info=True)
        return None





