import sys, logging, platform, subprocess, shutil

from pathlib import Path
from platformdirs import user_log_dir
from logging.handlers import RotatingFileHandler


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
        dir = Path(user_log_dir(filename.stem, appauthor=False))
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
    """A console that tails a log file"""
    def __init__(self, log_file: Path):
        self.log_file = str(log_file)
        self.viewer_process = None

    def open(self):
        
        if self.viewer_process and self.viewer_process.poll() is None:
            return  # already open

        system = platform.system()

        if system == "Windows":
            cmd = [
                "powershell",
                "-NoExit",
                "-Command",
                f'Get-Content -Path "{self.log_file}" -Wait -Tail 0'
            ]
            self.viewer_process = subprocess.Popen(
                cmd, creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            if self.viewer_process.poll() is not None:
                raise RuntimeError("Failed to launch trailing console process")

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

    

