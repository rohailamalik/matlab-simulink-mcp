from pathlib import Path
from project_root import root_path


def get_path(relative_path: str) -> Path:
    return root_path / relative_path


def get_cwd(eng) -> Path:
    try:
        return Path(str(eng.pwd(nargout=1)))
    except Exception as e:
        raise RuntimeError(f"Unexpected error while getting current working directory: {e}")

