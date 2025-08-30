import re
from pathlib import Path
from matlab_simulink_mcp.core.state import get_state


def check_for_commands(code: str):
    """Checks a given code string for forbidden commands and raises error if any found."""
    clean_code = code.lower()

    blacklist = get_state().blacklist

    for flag in blacklist:
        if re.search(flag, clean_code):
            return f"Use of {re.sub(r'^\\b|\\b$', '', flag).replace(r'\.', '.')} command is not allowed."

def check_for_paths(code: str):
    """Checks string literals in code for forbidden path usage and raises error if found."""
    
    literals = re.findall(r"(?:'[^']*'|\"[^\"]*\")", code)

    for literal in literals:
        path_str = literal[1:-1] 
        if not path_str:
            continue

        path = Path(path_str)

        if path.is_absolute():
            return "Absolute paths are not allowed. Only files on MATLAB path are accessible."

        if ".." in path.parts:
            return "Paths with .. are not allowed. Only files on MATLAB path are accessible."

        if "*" in path_str or "?" in path_str:
            return "Paths with * or ? are not allowed."

def check_code(code: str):
    """Checks a given code string for forbidden commands or paths and raises error if any found."""
    issues = check_for_commands(code) or check_for_paths(code)
    if issues:
        raise PermissionError(issues)
    
def check_path(file: str):
    """Checks a given file path for absolute or parent paths and raises error if found."""
    f = Path(file)
    if f.is_absolute() or ".." in f.parts:
        raise PermissionError("Access to absolute or parent paths is forbidden. Only files on MATLAB path are usable.")