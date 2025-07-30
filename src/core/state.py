from dataclasses import dataclass
from typing import Optional
import matlab.engine 

@dataclass
class ServerState:
    session_name: Optional[str] = None
    eng: Optional[matlab.engine.MatlabEngine] = None
    sl_lib_data: Optional[dict] = None
    

server_state = ServerState()

def get_engine():
    if server_state.eng is None:
        raise RuntimeError("MATLAB engine is not started. Please start the server first.")
    return server_state.eng


def get_sl_lib_data():
    if server_state.sl_lib_data is None:
        raise RuntimeError("Server data is not loaded. Please start the server first.")
    return server_state.sl_lib_data
