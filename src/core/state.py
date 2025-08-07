from dataclasses import dataclass, field, fields
from typing import Optional, List
import matlab.engine
import re
from core.startup import load_blacklist, load_simlib_data, set_helpers, set_sandbox, connect_session

@dataclass
class ServerState:
    """Global state for a MATLAB MCP session."""
    session: Optional[str] = None
    eng: Optional[matlab.engine.MatlabEngine] = None
    simlib: Optional[dict] = None
    blacklist: Optional[List[re.Pattern]] = None
    sandbox: bool = False # will be removed. too volatile

    def validate(self):
        """Ensures all attributes are set."""
        for f in fields(self):
            if getattr(self, f.name) is None:
                raise ValueError(f"Required attribute '{f.name}' is not set.")
            
    def set(self, session):
        """Sets up the state for a given session."""
        self.session = session
        self.eng = connect_session(self.session)
        self.simlib = load_simlib_data()
        self.blacklist = load_blacklist()
        set_helpers(self.eng)


state = ServerState()

def get_state() -> ServerState:
    return state


