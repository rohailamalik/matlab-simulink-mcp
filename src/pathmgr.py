# This file is for setting up the project directory based paths
# It is used to resolve relative paths in the project
# It should always be placed at the root of the project directory
# Do not delete

import sys
from pathlib import Path

def get_root() -> Path:
    if getattr(sys, 'frozen', False): 
        return Path(sys._MEIPASS)  
    return Path(__file__).resolve().parent

_root = get_root()

def get_path(relative_path: str) -> Path:
    return _root / relative_path