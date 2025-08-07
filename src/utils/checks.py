import re
from pathlib import Path
from typing import Literal
from core.state import get_state
from utils.utils import get_cwd


def check_file_name(file_name: str, extension: str, mode: Literal["read", "write"], overwrite: bool) -> Path:
    
    path = Path(file_name)

    if (path.is_absolute() or any(part == ".." for part in path.parts)):
        raise PermissionError("Access to absolute or parent paths is forbidden. Only files on MATLAB path are usable.")

    if path.suffix != extension:
        raise ValueError(f"Only {extension} files are supported.")

    eng = get_state().eng
    cwd = get_cwd(eng)

    path = cwd / path
    
    if mode == "write":
        if not path.stem.isidentifier():
            raise ValueError("File name must be a valid MATLAB identifier.")
        if not overwrite and path.is_file():
            raise RuntimeError(f"'{path}' already exists in MATLAB's current working directory.")
    elif mode == "read":
        if not path.is_file():
            raise FileNotFoundError(f"'{path}' not found in MATLAB's current working directory: {cwd}")
    
    return path


def check_commands(code: str) -> None:
    """Checks a given code string for forbidden commands and raises error if any found."""
    clean_code = code.lower()

    blacklist = get_state().blacklist

    for flag in blacklist:
        if re.search(flag, clean_code):
            raise PermissionError(f"Use of {re.sub(r'^\\b|\\b$', '', flag).replace(r'\.', '.')} command is not allowed")
        
    return None


def check_paths(code: str) -> None:
    """Checks string literals in code for forbidden path usage and raises error if found."""
    
    literals = re.findall(r"(?:'[^']*'|\"[^\"]*\")", code)

    for literal in literals:
        path_str = literal[1:-1] 
        if not path_str:
            continue

        path = Path(path_str)

        if path.is_absolute():
            raise PermissionError("Absolute paths are not allowed. Only files on MATLAB path are accessible.")

        if ".." in path.parts:
            raise PermissionError("Paths with .. are not allowed. Only files on MATLAB path are accessible.")

        if "*" in path_str or "?" in path_str:
            raise PermissionError("Paths with * or ? are not allowed.")

    return None


def check_code(code: str) -> None:
    return check_commands(code) or check_paths(code)