from project_root import root_path
from pathlib import Path

def get_path(relative_path: str) -> Path:
    return root_path / relative_path