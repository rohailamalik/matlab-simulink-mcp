import re
import json
import sys
import matlab.engine 

from typing import Any 
from pathlib import Path
from importlib import resources
from dataclasses import dataclass

from logger import logger


@dataclass
class MatlabState:
    session: str | None = None
    eng: matlab.engine.MatlabEngine | None = None
    helpers: Path | None = None
    simlib: dict | None = None
    blacklist: list[re.Pattern] | None = None

    def load_data(self):
        #self.simlib = json.loads((resources.files(data) / "simlib_db.json").read_text())
        #self.blacklist = to_regex_list((resources.files(data) / "blacklist.txt").read_text())
        self.simlib = {}
        self.blacklist = []

    def connect_matlab(self): 
        sessions = matlab.engine.find_matlab() or []
        if not sessions:
            logger.warning("No shared sessions found. Starting server without an engine. " \
            "Run matlab.engine.shareEngine in MATLAB to share a session and reconnect tool to reconnect.")
        else: 
            self.session = sessions[0]
            self.eng = matlab.engine.connect_matlab(self.session)
            self.add_helpers()
            logger.info(f"Connected to MATLAB session: {self.session}")

    def add_helpers(self):
        if getattr(sys, "frozen", False):
            pth = Path(sys._MEIPASS) / "matlab_simulink_mcp" / "data/helpers"
        #else:
        #    pth = Path(matlab_simulink_mcp.__file__).resolve().parent / "data/helpers"
        #self.eng.addpath(str(pth), nargout=0)
        #self.helpers = Path(pth)

_state = MatlabState()

def get_state() -> MatlabState:
    return _state




