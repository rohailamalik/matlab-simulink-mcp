import re
import json
import matlab.engine
from typing import List
from config.settings import settings
from utils.logger import logger
from utils.converters import cmd_to_regex
from pathmgr import get_path


def search_sessions() -> list:
    """Searches and returns a list of shared MATLAB sessions."""
    try:
        return matlab.engine.find_matlab()
    except Exception as e:
        raise RuntimeError(f"Error searching for MATLAB sessions: {e}")


def connect_session(session: str):
    """Connects to a shared MATLAB sessions."""
    try: 
        eng = matlab.engine.connect_matlab(session)
        logger.info(f"Connected to {session}")
        return eng
    except matlab.engine.EngineError as e:
        raise RuntimeError(f"Failed to connect to MATLAB session {session}: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during MATLAB connection: {e}")
    

def load_simlib_data() -> dict:
    """Loads the dictionary based data for Simulink model library"""

    path = settings.simlib_database_path
    
    if not path:
        raise ValueError("Simulink Library data file path not configured.")
    
    path = get_path(path)

    try:
        with path.open("r", encoding="utf-8") as f:
            content = json.load(f)
            logger.info(f"Simulink Library data loaded from {path}")
            return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Simulink Library data file not found in {path}")
    except json.JSONDecodeError:
        raise TypeError(f"Invalid JSON format for Simulink Library data file.")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while loading server Simulink Library data: {e}")
    

def load_blacklist() -> List[re.Pattern]:
    """Loads blacklisted commands from a text file, ignoring comments and empty lines."""

    path = settings.blacklist_commands_path
    path = get_path(path)

    try:
        patterns = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                pattern = cmd_to_regex(stripped)
                patterns.append(pattern)

        logger.info(f"Blacklist loaded from {path}")
        return patterns
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Blacklisted commands file not found in {path}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while loading blacklisted commands: {e}")
        

def set_helpers(eng):
    """Add MATLAB helper functions used in the tools to the MATLAB path"""

    path = settings.matlab_helpers_path
    path = get_path(path)

    if not path:
        raise ValueError("MATLAB helpers path not configured.")

    if not path.is_dir():
        raise FileNotFoundError(f"MATLAB helpers directory not found: {path}")

    try:
        eng.addpath(str(path), nargout=0)
        logger.info(f"Helpers path set to {path}")
    except Exception as e:
        raise RuntimeError("Failed to add MATLAB helper path: {e}")




