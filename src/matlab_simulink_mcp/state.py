import os
import json
import sys
import asyncio

from pathlib import Path
from importlib import resources
from dotenv import load_dotenv
from dataclasses import dataclass
from contextlib import asynccontextmanager
from fastmcp.server.dependencies import get_context

import matlab_simulink_mcp
from matlab_simulink_mcp import data
from matlab_simulink_mcp.log_utils import get_full_path, create_log_file, create_logger, create_console 
from matlab_simulink_mcp.eng_installer import import_engine, install_engine

console = False

load_dotenv()
matlab_dir = get_full_path(matlab_simulink_mcp, os.getenv("MATLAB_DIR"))
log_dir = get_full_path(matlab_simulink_mcp, os.getenv("LOG_DIR"))

log_file = create_log_file(filename=matlab_simulink_mcp.__name__, dir=log_dir)
logger = create_logger(name=matlab_simulink_mcp.__name__, log_file=log_file)
log_console = create_console(log_file=log_file)


def ensure_engine(matlab_dir):
    try:
        if not import_engine():
            logger.info("Could not find MATLAB engine package in the current envinronment.")

            logger.info(f"Installing MATLAB engine package from MATLAB installation.")
            if not matlab_dir:
                logger.info("MATLAB installation directory not specified. Searching in default directories.")
            logger.info(f"Waiting for access permissions by the user.")
            install_engine(matlab_dir)

            if not import_engine():
                raise RuntimeError("MATLAB Engine package still not available after attempted install.")
            logger.info("MATLAB engine package successfully installed.")

    except Exception as e:
        logger.error("You can try installing MATLAB engine package manually. See https://pypi.org/project/matlabengine/ for details.")
        raise e


@dataclass
class MatlabState:
    session: str | None = None
    eng = None # Don't put typehint here since engine may not be installed
    helpers: Path | None = None
    simlib: dict | None = None
    blacklist: set[str] | None = None

    def initialize(self):
        self._load_data()
        self.connect_matlab()

    def _load_data(self):
        self.simlib = json.loads((resources.files(data) / "simlib_db.json").read_text())
        self.blacklist = {
            line.strip().lower()
            for line in (resources.files(data) / "blacklist.txt").read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
            } 

    def connect_matlab(self):
        import matlab.engine 
        sessions = matlab.engine.find_matlab() or []
        if sessions:
            self.session = sessions[0]
            self.eng = matlab.engine.connect_matlab(self.session)
            self.helpers = self._add_helpers()

    def _add_helpers(self):
        if getattr(sys, "frozen", False):
            pth = Path(sys._MEIPASS) / "matlab_simulink_mcp" / "data/helpers"
        else:
            pth = get_full_path(matlab_simulink_mcp, "data/helpers")
        self.eng.addpath(str(pth), nargout=0)
        return Path(pth)


@asynccontextmanager
async def lifespan(server): # do not remove server argument as it will break stuff
    try:
        log_console.open()
        ensure_engine(matlab_dir=matlab_dir)
        state = MatlabState()
        await asyncio.to_thread(state.initialize)
        if state.eng is None:
            logger.warning("Starting server without an engine. " \
            "Run matlab.engine.shareEngine in MATLAB to share a session and access_matlab tool to reconnect.")
        else:
            logger.info(f"Connected to MATLAB session: {state.session}.")
            logger.info(f"Logging to: {log_file}")
        if not console:
            log_console.close()
        yield state
    except Exception as e:
        raise e


def get_state() -> dict:
    return get_context().request_context.lifespan_context



    





