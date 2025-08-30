import re
import json
import sys
import asyncio
import matlab.engine 

from pathlib import Path
from importlib import resources
from dataclasses import dataclass
from contextlib import asynccontextmanager
from fastmcp.server.dependencies import get_context
from fastmcp.exceptions import ToolError

import matlab_simulink_mcp
from matlab_simulink_mcp import data
from matlab_simulink_mcp.utils.logger import logger
from matlab_simulink_mcp.utils.convert import to_regex_list


@dataclass
class MatlabState:
    session: str | None = None
    eng: matlab.engine.MatlabEngine | None = None
    helpers: Path | None = None
    simlib: dict | None = None
    blacklist: list[re.Pattern] | None = None

    def load_data(self):
        self.simlib = json.loads((resources.files(data) / "simlib_db.json").read_text())
        self.blacklist = to_regex_list((resources.files(data) / "blacklist.txt").read_text())

    def connect_matlab(self): 
        sessions = matlab.engine.find_matlab() or []
        if not sessions:
            logger.warning("No shared sessions found. Starting server without an engine. " \
            "Run matlab.engine.shareEngine in MATLAB to share a session and reconnect tool to reconnect.")
        else: 
            self.session = sessions[0]
            self.eng = matlab.engine.connect_matlab(self.session)
            if self.eng is not None:
                self.add_helpers()
                logger.info(f"Connected to MATLAB session: {self.session}")

    def add_helpers(self):
        if getattr(sys, "frozen", False):
            pth = Path(sys._MEIPASS) / "matlab_simulink_mcp" / "data/helpers"
        else:
            pth = Path(matlab_simulink_mcp.__file__).resolve().parent / "data/helpers"
        self.eng.addpath(str(pth), nargout=0)
        self.helpers = Path(pth)


@asynccontextmanager
async def lifespan(server): # do not remove server argument as it will break stuff
    try:
        state = MatlabState()
        state.load_data()
        await asyncio.to_thread(state.connect_matlab)
        yield state
    except Exception as e:
        logger.error(f"Failed to initialize state: {e}")
        raise

def get_state() -> dict:
    return get_context().request_context.lifespan_context


def get_engine() -> matlab.engine.MatlabEngine:
    eng = get_state().eng
    if eng is None:
        raise ToolError("Could not access MATLAB. Ask user to run matlab.engine.shareEngine"
        " in MATLAB, and then use reconnect tool to reconnect.")
    return eng 
    





