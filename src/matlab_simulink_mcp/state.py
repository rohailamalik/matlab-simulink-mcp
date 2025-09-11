import os, types, json, sys

from pathlib import Path
from importlib import resources
from dataclasses import dataclass
from dotenv import load_dotenv

import matlab_simulink_mcp
from matlab_simulink_mcp import data
from matlab_simulink_mcp.log_utils import create_log_file, create_logger, create_console 


def get_full_path(pkg: types.ModuleType, path: str | Path) -> Path:
    if path is None:
        return None
    path = Path(path)
    if path.is_absolute():
        return path
    return (Path(pkg.__file__).resolve().parent / path).resolve()

load_dotenv()
log_dir = get_full_path(matlab_simulink_mcp, os.getenv("LOG_DIR"))

log_file = create_log_file(filename=matlab_simulink_mcp.__name__, dir=log_dir)
log_console = create_console(log_file=log_file)
logger = create_logger(name=matlab_simulink_mcp.__name__, log_file=log_file)


@dataclass
class EngineState:
    installed: int = 0
    session: str | None = None
    eng = None # Don't put typehint here since engine may not be installed
    helpers: Path | None = None
    simlib: dict | None = None
    blacklist: set[str] | None = None

    def initialize(self):
        self.ensure_engine()
    
        if self.installed == 1:
            self.connect_engine()
            self.load_data()

            if self.eng is None:
                logger.warning("Starting server without an engine. " \
                "Run matlab.engine.shareEngine in MATLAB to share a session and access_matlab tool to reconnect.")
            else:
                logger.info(f"Connected to MATLAB session: {self.session}.")
                logger.info(f"Logging to: {log_file}")

    def load_data(self):
        self.simlib = json.loads((resources.files(data) / "simlib_db.json").read_text())
        self.blacklist = {
            line.strip().lower()
            for line in (resources.files(data) / "blacklist.txt").read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
            } 
    
    def connect_engine(self):
        if self.installed == 1:
            import matlab.engine
            sessions = matlab.engine.find_matlab() or []
            if sessions:
                self.session = sessions[0]
                self.eng = matlab.engine.connect_matlab(self.session)
                self.helpers = self.add_helpers()

    def add_helpers(self):
        if getattr(sys, "frozen", False):
            pth = Path(sys._MEIPASS) / "matlab_simulink_mcp" / "data/helpers"
        else:
            pth = get_full_path(matlab_simulink_mcp, "data/helpers")
        self.eng.addpath(str(pth), nargout=0)
        return Path(pth)
    
    def ensure_engine(self):
        try:
            import matlab.engine 
        except ImportError:
            logger.info("MATLAB Engine for Python package not found. Starting package installer...")
            import matlab_simulink_mcp.installer.launcher as launcher
            self.installed = launcher.run()
            if self.installed == 1:
                try:
                    import matlab.engine
                    logger.info("MATLAB engine package successfully installed.")
                except ImportError:
                    raise ImportError("MATLAB Engine package not available even after attempted install.")
            elif self.installed != -1:
                raise RuntimeError("Failed to install MATLAB engine package. " \
                "This server requires MATLAB engine package to work.. " \
                "You can try installing it manually from PyPi or your MATLAB installation.")
            

    
    



    





