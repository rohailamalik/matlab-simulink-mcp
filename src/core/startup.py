import re
import json
import matlab.engine
from typing import Optional, List # Optional is used in state.py through import *
from pathlib import Path 
from utils.logger import logger
from utils.converters import cmd_to_regex
from pathfinder import get_path


def search_sessions() -> list:
    """Searches and returns a list of shared MATLAB sessions."""
    try:
        logger.info("Searching for shared MATLAB sessions...")
        return matlab.engine.find_matlab()
    except Exception as e:
        raise RuntimeError(f"Error searching for MATLAB sessions: {e}")
    

def select_session():
    """Select a MATLAB session from available shared sessions."""
    while True:
        sessions = search_sessions() or []
        if not sessions:
            logger.info(
                "No shared sessions found. "
                "Run `matlab.engine.shareEngine` in MATLAB to share a session."
            )
            input("Press Enter to retry...")
            continue

        if len(sessions) == 1:
            return sessions[0]

        logger.info("Multiple shared sessions found:")
        for i, s in enumerate(sessions, 1):
            logger.info(f"  {i}. {s}")

        while True:
            choice = input("Select a session by typing its index: ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(sessions):
                    return sessions[idx - 1]
            logger.info("Invalid choice. Please enter a valid number.")


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
    

def load_simlib(path: Path) -> dict:
    """Loads the dictionary based data for Simulink model library"""
    
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
    

def load_blacklist(path: Path) -> List[re.Pattern]:
    """Loads blacklisted commands from a text file, ignoring comments and empty lines."""

    if not path:
        raise ValueError("Blacklist file path not configured.")
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
        

def set_helpers(path: Path, eng):
    """Add MATLAB helper functions used in the tools to the MATLAB path"""

    if not path:
        raise ValueError("Helper functions path not configured.")
    path = get_path(path)

    if not path.is_dir():
        raise FileNotFoundError(f"MATLAB helpers directory not found: {path}")

    try:
        eng.addpath(str(path), nargout=0)
        logger.info(f"Helpers path set to {path}")
        return path
    except Exception as e:
        raise RuntimeError("Failed to add MATLAB helper path: {e}")




