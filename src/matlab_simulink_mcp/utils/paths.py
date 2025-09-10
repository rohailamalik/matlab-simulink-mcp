import types
from pathlib import Path


def get_full_path(pkg: types.ModuleType, path: str | Path) -> Path:
    """Absolutizes a relative path to the provided package. Returns as is if the path is already absolute."""
    if path is None:
        return None
    path = Path(path)
    if path.is_absolute():
        return path
    return (Path(pkg.__file__).resolve().parent / path).resolve()