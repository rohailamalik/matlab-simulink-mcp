import sys
from pathlib import Path

def get_base_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(sys.modules['__main__'].__file__).resolve().parent

def get_path(relative_path: str) -> Path:
    return get_base_path() / relative_path