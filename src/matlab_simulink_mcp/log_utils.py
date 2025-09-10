import sys
import logging
import platform
import subprocess
import shutil
import types

from pathlib import Path
from platformdirs import user_log_dir
from logging.handlers import RotatingFileHandler


def get_full_path(pkg: types.ModuleType, path: str | Path) -> Path:
    """Absolutizes a relative path to the provided package. Returns as is if the path is already absolute."""
    if path is None:
        return None
    path = Path(path)
    if path.is_absolute():
        return path
    return (Path(pkg.__file__).resolve().parent / path).resolve()


def create_log_file(filename: str, dir: Path | None) -> Path:
    """Creates a log file in the given directory or user log directory (if former fails or isn't specified)."""

    filename = Path(filename)
    if filename.suffix != ".log":
        filename = filename.with_suffix(".log")

    if dir:
        try:
            dir = Path(dir)
            dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            dir = None

    if dir is None:
        dir = user_log_dir(filename.stem, appauthor=False)
        dir.mkdir(parents=True, exist_ok=True)

    return dir / filename


def create_logger(name: str, log_file: Path) -> logging.Logger:
    """Sets up a logger with stderr console and rotating file handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


class TrailingConsole:
    def __init__(self, log_file: Path):
        self.log_file = log_file

    def open(self):
        """Open a console window that tails the log file."""

        system = platform.system()

        if system == "Windows":
            self.viewer_process = subprocess.Popen(
                [
                    "powershell", "-NoExit", "-Command",
                    f"Get-Content -Path {self.log_file} -Wait -Tail 0"
                ],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

        elif system == "Linux":
            candidates = [
                "x-terminal-emulator",
                "gnome-terminal",
                "konsole",
                "xfce4-terminal",
                "xterm",
            ]
            terminal = next((t for t in candidates if shutil.which(t)), None)

            if terminal is None:
                self.logger.error("No supported terminal emulator found for log viewer.")
                return

            self.viewer_process = subprocess.Popen([terminal, "-e", f"tail -n 0 -f '{self.log_file}'"])

        elif system == "Darwin":  # macOS
            full_cmd = f"tail -n 0 -f '{self.log_file}'"
            subprocess.run([
                "osascript", "-e",
                f'tell application "Terminal" to do script "{full_cmd}"'
            ])
            self.viewer_process = None

    def close(self):
        if self.viewer_process and self.viewer_process.poll() is None:
            self.viewer_process.terminate()
            self.viewer_process = None


def create_console(log_file: Path) -> TrailingConsole:
    return TrailingConsole(log_file)

    

