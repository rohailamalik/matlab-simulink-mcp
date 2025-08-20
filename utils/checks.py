import re
from pathlib import Path
from core.state import get_state
from utils.utils import err


def check_file(eng, file: str, write: bool = False, overwrite: bool = False, adv: bool = True) -> dict | None:
    """Validate a MATLAB file operation before use."""
    p = Path(file)

    if p.is_absolute() or ".." in p.parts:
        return err("Access to absolute or parent paths is forbidden. Only files on MATLAB path are usable.", security=True)

    if adv:
        try:
            exists = eng.exist(file, nargout=1)
        except Exception:
            return err("Error checking if the file exists.")

        if write:
            if not p.stem.isidentifier():
                return err("File name must be a valid MATLAB identifier.", log=False)
            if exists == 2 and not overwrite:
                return err(f"'{file}' already exists in MATLAB's current working directory or on the MATLAB path.", log=False)
        else:
            if exists == 0:
                return err(f"'{file}' not found in MATLAB's current working directory or on the MATLAB path.", log=False)

    return None


def check_commands(code: str) -> dict | None:
    """Checks a given code string for forbidden commands and raises error if any found."""
    clean_code = code.lower()

    blacklist = get_state().blacklist

    for flag in blacklist:
        if re.search(flag, clean_code):
            return err(f"Use of {re.sub(r'^\\b|\\b$', '', flag).replace(r'\.', '.')} command is not allowed.", security = True)
        
    return None


def check_paths(code: str) -> dict | None:
    """Checks string literals in code for forbidden path usage and raises error if found."""
    
    literals = re.findall(r"(?:'[^']*'|\"[^\"]*\")", code)

    for literal in literals:
        path_str = literal[1:-1] 
        if not path_str:
            continue

        path = Path(path_str)

        if path.is_absolute():
            return err("Absolute paths are not allowed. Only files on MATLAB path are accessible.", security = True)

        if ".." in path.parts:
            return err("Paths with .. are not allowed. Only files on MATLAB path are accessible.", security = True)

        if "*" in path_str or "?" in path_str:
            return err("Paths with * or ? are not allowed.", security = True)

    return None


def check_code(code: str) -> dict | None:
    return check_commands(code) or check_paths(code)