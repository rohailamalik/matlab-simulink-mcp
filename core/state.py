from dataclasses import dataclass, fields
from config.settings import settings
from core.startup import *

@dataclass
class ServerState:
    """Global state for session."""
    session: str | None = None
    eng: matlab.engine.MatlabEngine | None = None
    simlib: dict | None = None
    blacklist: list[re.Pattern] | None = None
    helpers: Path | None = None
            
    def initialize(self):
        """Initializes the state."""
        self.session = select_session()
        self.eng = connect_session(self.session)
        self.simlib = load_simlib(settings.simlib_database_path)
        self.blacklist = load_blacklist(settings.blacklist_commands_path)
        self.helpers = set_helpers(settings.matlab_helpers_path, self.eng)

    def validate(self):
        """Ensures all attributes are set."""
        for f in fields(self):
            if getattr(self, f.name) is None:
                raise ValueError(f"Incomplete state. '{f.name}' is not set.")
    

_state = ServerState()

def init_state():
    _state.initialize()
    _state.validate()

def get_state() -> ServerState:
    return _state

# TODO: Incorporate a check engine function and run it on a separate thread on loop





