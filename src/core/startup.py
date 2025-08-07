import re
import json
import matlab.engine
from typing import List
from config.settings import settings
from utils.utils import get_path
from utils.converters import cmd_to_regex


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
        return eng
    except matlab.engine.EngineError as e:
        raise RuntimeError(f"Failed to connect to MATLAB session {session}: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during MATLAB connection: {e}")
    

def load_simlib_data() -> dict:
    """Loads the dictionary based data for Simulink model library"""

    simlib_path = settings.simlib_database_path
    
    if not simlib_path:
        raise ValueError("Simulink Library data file path not configured.")

    path = get_path(simlib_path)

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Simulink Library data file not found in {path}")
    except json.JSONDecodeError:
        raise TypeError(f"Invalid JSON format for Simulink Library data file.")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while loading server Simulink Library data: {e}")
    

def load_blacklist() -> List[re.Pattern]:
    """Loads blacklisted commands from a text file, ignoring comments and empty lines."""

    path = settings.blacklist_commands_path

    try:
        patterns = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                pattern = cmd_to_regex(stripped)
                patterns.append(pattern)
        return patterns
    except FileNotFoundError:
        raise FileNotFoundError(f"Blacklisted commands file not found in {path}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while loading blacklisted commands: {e}")


def set_sandbox(eng) -> bool:
    """Sets up the sandbox mode (high security, wrapping all interactions with files)"""

    wrappers_path = settings.security_wrappers_path

    if not wrappers_path:
        raise ValueError("MATLAB security wrappers path not configured.")
    
    path = get_path(wrappers_path)

    try: 
        if settings.sandbox:
            eng.addpath(str(path), '-begin', nargout=0)
        else: 
            eng.builtin('rmpath', str(path), nargout=0)
    except Exception as e:
        raise RuntimeError(f"Unexpected error while setting up sandbox mode: {e}")
    
    return settings.sandbox
        

def set_helpers(eng):
    """Add MATLAB helper functions used in the tools to the MATLAB path"""

    helpers_path = settings.matlab_helpers_path

    if not helpers_path:
        raise ValueError("MATLAB helpers path not configured.")

    path = get_path(helpers_path)

    if not path.is_dir():
        raise FileNotFoundError(f"MATLAB helpers directory not found: {path}")

    try:
        eng.addpath(str(path), nargout=0)
    except Exception as e:
        raise RuntimeError("Failed to add MATLAB helper path: {e}")




