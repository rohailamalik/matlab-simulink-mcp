import json
import sys

from pathlib import Path
from importlib import resources
from dataclasses import dataclass

import matlab_simulink_mcp
from matlab_simulink_mcp import data
from matlab_simulink_mcp.config import logger, log_file, matlab_dir
from matlab_simulink_mcp.utils.paths import get_full_path
from matlab_simulink_mcp.engine.installer import import_engine, install_engine


@dataclass
class EngineState:
    session: str | None = None
    eng = None # Don't put typehint here since engine may not be installed
    helpers: Path | None = None
    simlib: dict | None = None
    blacklist: set[str] | None = None

    def initialize(self):
        self.ensure_engine(matlab_dir)
        self.load_data()
        self.connect_engine()
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
    
    def ensure_engine(self, matlab_dir):
        try:
            if not import_engine():
                logger.info("Could not find MATLAB engine package in the current envinronment.")
                install_engine(matlab_dir)
                if not import_engine():
                    raise RuntimeError("MATLAB Engine package not available even after attempted install.")
                logger.info("MATLAB engine package successfully installed.")
        except Exception:
            logger.error("You can try installing MATLAB engine package manually. See https://pypi.org/project/matlabengine/ for details.")
            raise 




    





