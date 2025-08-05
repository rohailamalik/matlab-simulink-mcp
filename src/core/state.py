from dataclasses import dataclass
from typing import Optional, Literal
import matlab.engine 
from pathlib import Path

@dataclass
class ServerState:
    session: Optional[str] = None
    eng: Optional[matlab.engine.MatlabEngine] = None
    sl_lib_data: Optional[dict] = None
    helpers_path: Optional[Path] = None
    security_wrappers_path: Optional[Path] = None
    cwd: Optional[Path] = None
    advanced_security: bool = False


server_state = ServerState()


def get_state(key: str):
     
     if not hasattr(server_state, key):
        raise AttributeError(f"'{key}' is not a valid state attribute.")

     value = getattr(server_state, key)
     
     if value is None:
        raise ValueError(f"'{key}' has not been set yet.")
     
     return value

