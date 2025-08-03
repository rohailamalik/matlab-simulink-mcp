from dataclasses import dataclass
from typing import Optional
import matlab.engine 

@dataclass
class ServerState:
    session: Optional[str] = None
    eng: Optional[matlab.engine.MatlabEngine] = None
    sl_lib_data: Optional[dict] = None
    canvas_path: Optional[str] = None
    helpers_path: Optional[str] = None
    

server_state = ServerState()

def get_state(key: str):
     
     if not hasattr(server_state, key):
        raise AttributeError(f"'{key}' is not a valid key.")

     value = getattr(server_state, key)
     
     if value is None:
        raise ValueError(f"'{key}' has not been set yet.")
     
     return value


def get_engine():
    if server_state.eng is None:
        raise RuntimeError("MATLAB engine is not started. Please start the server first.")
    return server_state.eng


def get_sl_lib_data():
    if server_state.sl_lib_data is None:
        raise RuntimeError("Server data is not loaded. Please start the server first.")
    return server_state.sl_lib_data


