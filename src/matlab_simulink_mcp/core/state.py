import re
import json
import matlab.engine 

from typing import Any 
from pathlib import Path
from importlib import resources
from dataclasses import dataclass, fields

from matlab_simulink_mcp import data
from matlab_simulink_mcp.utils.convert import to_regex_list


@dataclass
class SessionState:
    session: str | None = None
    eng: matlab.engine.MatlabEngine | None = None
    simlib: dict | None = None
    blacklist: list[re.Pattern] | None = None
    helpers: Path | None = None

    def initialize(self, session):
        self.session = session 
        self.connect_session() 
        self.load_simlib() 
        self.load_blacklist() 
        self.load_helpers() 

    def connect_session(self):
        self.eng = matlab.engine.connect_matlab(self.session)
    
    def load_simlib(self) -> dict[str, Any]:
        self.simlib = json.loads((resources.files(data) / "simlib_db.json").read_text())
    
    def load_blacklist(self) -> list[re.Pattern]:
        self.blacklist = to_regex_list((resources.files(data) / "blacklist.txt").read_text())
    
    def load_helpers(self) -> Path:
        path = str(resources.as_file(data) / "helpers")
        self.eng.addpath(str(path), nargout=0)
        self.helpers = Path(path)
            
    def validate(self):
        for f in fields(self):
            if getattr(self, f.name) is None:
                raise ValueError(f"Incomplete state. '{f.name}' is not set.")

_state = SessionState()


def get_state() -> SessionState:
    return _state


def get_cwd() -> Path:
    try:
        eng = get_state().eng
        return Path(str(eng.pwd(nargout=1)))
    except Exception as e:
        raise RuntimeError(f"Error getting current working directory: {e}")

# TODO: Incorporate a check engine function and run it on a separate thread on loop





