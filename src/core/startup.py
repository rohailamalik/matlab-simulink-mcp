from config.settings import settings
from utils.logger import logger
from utils.utils import get_path
import pickle 
import json
from typing import Optional
import tempfile
from pathlib import Path


def load_server_data() -> Optional[dict]:
    if not settings.sl_lib_data_path:
        logger.error("Server data path not configured.")
        return None

    sl_lib_data_path = get_path(settings.sl_lib_data_path)
    ext = sl_lib_data_path.suffix.lower()

    try:
        if ext == ".json":

            with open(sl_lib_data_path, "r", encoding="utf-8") as f:
                logger.info("Server data loaded from JSON.")
                return json.load(f)
        elif ext in (".pkl", ".pickle"):
            with open(sl_lib_data_path, "rb") as f:
                logger.info("Server data loaded from Pickle.")
                return pickle.load(f)
        else:
            logger.error(f"Unsupported server data file extension: {ext}")
    except FileNotFoundError:
        logger.error("Server data file not found.")
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in server data file.")
    except pickle.UnpicklingError:
        logger.error("Invalid Pickle format in server data file.")
    except Exception:
        logger.error("Unexpected error while loading server data", exc_info=True)


def set_helpers(eng) -> str:
    if not settings.matlab_helpers_path:
        logger.warning("MATLAB helpers path not set.")

    helpers_path = get_path(settings.matlab_helpers_path)

    if not helpers_path.is_dir():
        logger.error(f"MATLAB helpers directory not found: {helpers_path}")

    m_files = [f for f in helpers_path.iterdir() if f.suffix == ".m"]
    if not m_files:
        logger.warning(f"No .m files found in helpers directory: {helpers_path}")

    try:
        eng.addpath(str(helpers_path), nargout=0)
        logger.info("MATLAB helper functions added to path successfully.")
        return str(helpers_path)

    except Exception:
        logger.error("Failed to add MATLAB helper path", exc_info=True)


def set_up_canvas():
    """
    Returns path to a MATLAB script file in the temporary files directory.
    This is the file where any arbitrary code is executed.
    """
    return str(Path(tempfile.gettempdir()) / "canvas.m")

